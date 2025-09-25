from .database import SessionLocal
import logging

logger = logging.getLogger(__name__)

def get_db():
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        # Return a mock session or handle the error appropriately
        raise
    finally:
        try:
            db.close()
        except:
            pass
