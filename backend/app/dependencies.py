# ============================================================
# SHARED DEPENDENCIES
# ============================================================

from app.database import SessionLocal


def get_db():
    """
    FastAPI dependency that provides a database session.
    Automatically closes the session when the request is done.

    Usage in routes:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
