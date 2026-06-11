import logging
import re
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas_chat import ChatRequest, ChatResponse
from app.models import Product
from app.schemas import ProductResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Basic keyword dictionary to map natural language to categories
CATEGORY_MAP = {
    "dog": "Dog Food",
    "puppy": "Dog Food",
    "cat": "Cat Food",
    "kitten": "Cat Food",
    "bird": "Bird Care",
    "parrot": "Bird Care",
    "fish": "Aquarium",
    "aquarium": "Aquarium",
    "toy": "Toys",
    "play": "Toys",
    "ball": "Toys",
    "health": "Healthcare",
    "medicine": "Healthcare",
    "pill": "Healthcare",
    "sick": "Healthcare"
}

# FAQ Knowledge Base using Regex Patterns
FAQ_KNOWLEDGE_BASE = [
    {
        "patterns": [r"shipping", r"delivery", r"how long.*arrive", r"ship"],
        "answer": "We offer fast shipping! Orders are typically delivered within 2-3 business days. Free shipping is available on orders over ₹500."
    },
    {
        "patterns": [r"return", r"refund", r"exchange", r"money back"],
        "answer": "We have a hassle-free 14-day return policy. If you or your pet aren't satisfied, just reach out to us for a full refund or exchange."
    },
    {
        "patterns": [r"hours", r"open", r"close", r"time"],
        "answer": "Our physical retail stores are open every day from 9:00 AM to 9:00 PM. Our online store is open 24/7!"
    },
    {
        "patterns": [r"contact", r"support", r"help", r"phone", r"call"],
        "answer": "You can reach our support team at support@pawkart.in or call us at 1800-PAW-KART. We're always here to help!"
    },
    {
        "patterns": [r"discount", r"coupon", r"promo", r"offer", r"sale"],
        "answer": "We frequently run sales! Check the banners on our homepage for current promo codes. First-time buyers get 10% off with code WELCOME10."
    },
    {
        "patterns": [r"hello", r"hi", r"hey", r"greetings"],
        "answer": "Hello there! I'm the PawKart assistant. How can I help you and your furry friend today?"
    },
    {
        "patterns": [r"thank", r"thanks", r"appreciate"],
        "answer": "You're very welcome! Let me know if you need anything else."
    }
]

@router.post("/chat", response_model=ChatResponse)
def handle_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    NLP Customer Chatbot endpoint.
    Takes a natural language message, infers the category and FAQ intent, 
    and returns combined conversational responses and product recommendations.
    """
    message = request.message.lower()
    logger.info(f"Chat message received from customer {request.customer_id}: {message}")
    
    conversational_reply = ""
    
    # 1. FAQ Intent Extraction
    for faq in FAQ_KNOWLEDGE_BASE:
        for pattern in faq["patterns"]:
            if re.search(pattern, message):
                conversational_reply = faq["answer"]
                break
        if conversational_reply:
            break
            
    # 2. Product Category Extraction
    detected_category = None
    for keyword, category in CATEGORY_MAP.items():
        if keyword in message:
            detected_category = category
            break
            
    # 3. Database Querying & Response Formulation
    products = []
    
    if detected_category:
        db_products = db.query(Product).filter(
            Product.category == detected_category,
            Product.available == True
        ).limit(3).all()
        products = [ProductResponse.model_validate(p) for p in db_products]
        
        # Build combined reply
        if conversational_reply:
            reply = f"{conversational_reply}\n\nAlso, since you're looking for {detected_category}, I found these great options for you:"
        else:
            reply = f"I found some great options in {detected_category} for you! Check these out:"
            
    else:
        if conversational_reply:
            reply = conversational_reply
        else:
            # Generic recommendation fallback
            db_products = db.query(Product).filter(Product.available == True).limit(3).all()
            reply = "I'm not exactly sure what you're asking, but here are some of our most popular items!"
            products = [ProductResponse.model_validate(p) for p in db_products]
        
    return ChatResponse(
        reply=reply,
        suggested_products=products
    )
