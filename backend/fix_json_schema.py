"""
Emergency database schema fix for PostgreSQL JSON array literal error
This script will drop and recreate the ideas table with proper JSON column types
"""
import logging
import sys
from sqlalchemy import text, inspect
from database import engine, SessionLocal
from models import Base, Idea

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_existing_ideas():
    """Backup existing ideas before schema change"""
    db = SessionLocal()
    try:
        # Check if ideas table exists and has data
        inspector = inspect(engine)
        if 'ideas' not in inspector.get_table_names():
            logger.info("No existing ideas table found, no backup needed")
            return []
        
        # Get existing ideas
        result = db.execute(text("SELECT * FROM ideas"))
        ideas = result.fetchall()
        logger.info(f"Backed up {len(ideas)} existing ideas")
        return ideas
    except Exception as e:
        logger.error(f"Failed to backup ideas: {e}")
        return []
    finally:
        db.close()

def drop_and_recreate_tables():
    """Drop and recreate all tables with proper schema"""
    try:
        logger.info("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        logger.info("Creating tables with proper JSON schema...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Tables recreated successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to recreate tables: {e}")
        return False

def restore_ideas(backup_ideas):
    """Restore ideas with proper JSON formatting"""
    if not backup_ideas:
        logger.info("No ideas to restore")
        return
    
    db = SessionLocal()
    try:
        for idea_row in backup_ideas:
            # Create new idea with proper types
            new_idea = Idea(
                id=idea_row.id,
                title=idea_row.title,
                original_description=idea_row.original_description,
                tags=[] if not idea_row.tags else (idea_row.tags if isinstance(idea_row.tags, list) else []),
                status=idea_row.status,
                created_at=idea_row.created_at,
                updated_at=idea_row.updated_at
            )
            db.add(new_idea)
        
        db.commit()
        logger.info(f"✅ Restored {len(backup_ideas)} ideas")
    except Exception as e:
        logger.error(f"❌ Failed to restore ideas: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main migration function"""
    logger.info("🚀 Starting PostgreSQL JSON schema fix...")
    
    # Step 1: Backup existing data
    logger.info("Step 1: Backing up existing ideas...")
    backup_ideas = backup_existing_ideas()
    
    # Step 2: Drop and recreate tables
    logger.info("Step 2: Recreating tables with proper JSON schema...")
    if not drop_and_recreate_tables():
        logger.error("❌ Migration failed at table recreation")
        sys.exit(1)
    
    # Step 3: Restore data
    logger.info("Step 3: Restoring ideas with proper JSON formatting...")
    restore_ideas(backup_ideas)
    
    logger.info("🎉 Migration completed successfully!")
    logger.info("The ideas table now has proper PostgreSQL JSON columns")

if __name__ == "__main__":
    main()