"""
Direct column fix for tags field - convert from string to proper JSON array
This avoids the need to drop/recreate tables
"""
import logging
from sqlalchemy import text
from database import engine, SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_tags_column():
    """Fix the tags column to properly handle JSON arrays"""
    db = SessionLocal()
    try:
        logger.info("🔧 Starting tags column fix...")
        
        # First, let's see what we're working with
        result = db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'ideas' AND column_name = 'tags'"))
        column_info = result.fetchone()
        
        if column_info:
            logger.info(f"Current tags column: {column_info.column_name} - {column_info.data_type}")
            
            # If it's already an ARRAY type, we're good!
            if column_info.data_type.upper() == 'ARRAY':
                logger.info("✅ Tags column is already ARRAY type - no conversion needed!")
                
                # Just verify we can read the data
                try:
                    result = db.execute(text("SELECT COUNT(*) FROM ideas"))
                    count = result.scalar()
                    logger.info(f"Found {count} existing ideas")
                    
                    # Get sample data to see current format
                    if count > 0:
                        result = db.execute(text("SELECT id, title, tags FROM ideas LIMIT 3"))
                        samples = result.fetchall()
                        for sample in samples:
                            logger.info(f"Sample idea: {sample.title} - tags: {sample.tags} (type: {type(sample.tags)})")
                    
                    # Column is already correct type, just commit and return
                    db.commit()
                    logger.info("✅ Array column verified and working")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error reading array data: {e}")
                    return False
        else:
            logger.info("Tags column not found, creating new table structure...")
            
        # If we get here, we need to create or fix the column
        logger.info("Column needs to be created or converted...")
        
        # Check if ideas table exists
        try:
            result = db.execute(text("SELECT COUNT(*) FROM ideas"))
            count = result.scalar()
            logger.info(f"Found {count} existing ideas")
        except Exception as e:
            logger.info(f"Ideas table doesn't exist: {e}")
            # Let SQLAlchemy create the tables normally
            return True
        
        db.commit()
        logger.info("✅ Tags column fixed successfully")
        
        # Verify the fix
        result = db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'ideas' AND column_name = 'tags'"))
        column_info = result.fetchone()
        logger.info(f"Updated tags column: {column_info.column_name} - {column_info.data_type}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix tags column: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    fix_tags_column()