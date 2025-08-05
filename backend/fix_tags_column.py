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
        else:
            logger.info("Tags column not found, creating new table structure...")
            
        # Check if ideas table exists and what's in it
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
            
        except Exception as e:
            logger.info(f"Ideas table doesn't exist or is empty: {e}")
        
        # Now let's alter the column to be proper JSONB
        logger.info("Altering tags column to JSONB...")
        
        # First convert any string-encoded JSON to proper format
        db.execute(text("""
            UPDATE ideas 
            SET tags = CASE 
                WHEN tags::text LIKE '[%]' THEN tags::jsonb
                WHEN tags::text = '[]' THEN '[]'::jsonb
                ELSE '[]'::jsonb
            END
            WHERE tags IS NOT NULL
        """))
        
        # Alter the column type if needed
        db.execute(text("ALTER TABLE ideas ALTER COLUMN tags TYPE JSONB USING tags::jsonb"))
        
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