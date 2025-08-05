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

def clean_orphaned_tables():
    """Remove orphaned tables from old architecture that block table recreation"""
    db = SessionLocal()
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Define orphaned tables from old architecture
        orphaned_tables = ['conversations', 'build_plans', 'exports']
        
        for table in orphaned_tables:
            if table in existing_tables:
                logger.info(f"Dropping orphaned table: {table}")
                db.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
        
        db.commit()
        logger.info("✅ Orphaned tables cleaned up")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to clean orphaned tables: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def drop_and_recreate_tables():
    """Drop and recreate all tables with proper schema"""
    try:
        # First clean up orphaned tables that might block recreation
        logger.info("Cleaning up orphaned tables from old architecture...")
        if not clean_orphaned_tables():
            logger.error("Failed to clean orphaned tables, attempting CASCADE drop...")
        
        logger.info("Dropping existing tables with CASCADE...")
        # Use raw SQL with CASCADE to handle any remaining constraints
        db = SessionLocal()
        try:
            # Drop tables that we know exist in our current model
            tables_to_drop = ['plans', 'refinement_sessions', 'ideas']
            for table in tables_to_drop:
                db.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            db.commit()
            logger.info("✅ Tables dropped with CASCADE")
        except Exception as e:
            logger.error(f"Manual table drop failed: {e}")
            db.rollback()
            # Fall back to metadata drop
            Base.metadata.drop_all(bind=engine)
        finally:
            db.close()
        
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
        raise Exception("Migration failed at table recreation - check database permissions and constraints")
    
    # Step 3: Restore data
    logger.info("Step 3: Restoring ideas with proper JSON formatting...")
    restore_ideas(backup_ideas)
    
    logger.info("🎉 Migration completed successfully!")
    logger.info("The ideas table now has proper PostgreSQL JSON columns")

if __name__ == "__main__":
    main()