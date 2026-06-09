import os
import sys

# Ensure backend directory is in Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database import verify_and_update_schema
from app.ai import registry, init_models


def verify():
    print("====================================================")
    print("PAWKART PHASE 1 VERIFICATION START")
    print("====================================================")

    # 1. Database migration test
    print("\n[Step 1] Running database schema verification...")
    try:
        verify_and_update_schema()
        print("=> SUCCESS: Database schema verified and updated.")
    except Exception as e:
        print(f"=> ERROR: Database schema verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 2. Model initialization test
    print("\n[Step 2] Initializing registered models...")
    try:
        init_models()
        print("=> SUCCESS: Models initialized.")
    except Exception as e:
        print(f"=> ERROR: Model initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 3. Model registry check
    print("\n[Step 3] Checking model registry...")
    models = registry.list_models()
    print(f"Registered models: {models}")
    if "lstm" not in models:
        print("=> ERROR: 'lstm' is missing from registry.")
        return False
    
    lstm = registry.get_model("lstm")
    print(f"LSTM Loaded: {lstm.is_loaded}")
    print(f"LSTM Metadata: {lstm.get_model_summary()}")

    # 4. Check files
    print("\n[Step 4] Checking folder structure files...")
    ai_dir = os.path.join(os.path.dirname(__file__), "app", "ai")
    files_to_check = [
        os.path.join(ai_dir, "base.py"),
        os.path.join(ai_dir, "registry.py"),
        os.path.join(ai_dir, "evaluator.py"),
        os.path.join(ai_dir, "models", "lstm_model.py"),
    ]
    for filepath in files_to_check:
        basename = os.path.basename(filepath)
        if os.path.exists(filepath):
            print(f"  - {basename}: Exists")
        else:
            print(f"  - {basename}: MISSING!")
            return False

    print("\n====================================================")
    print("=> PHASE 1 VERIFICATION COMPLETED SUCCESSFULLY!")
    print("====================================================")
    return True


if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)
