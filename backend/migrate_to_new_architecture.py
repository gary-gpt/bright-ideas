"""
Database migration script for transitioning to new architecture
WARNING: This will create new tables for the new architecture
"""
import sys
import logging
from sqlalchemy import text
from database import engine, create_tables, check_database_connection
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """
    Migrate database to new architecture
    """
    logger.info("Starting database migration to new architecture...")
    
    # Check database connection
    if not check_database_connection():
        logger.error("Cannot connect to database. Please check your DATABASE_URL")
        return False
    
    try:
        # Create new tables
        logger.info("Creating new tables for structured refinement system...")
        create_tables()
        logger.info("✅ New tables created successfully")
        
        # Show current database status
        with engine.connect() as conn:
            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('ideas', 'refinement_sessions', 'plans')
                ORDER BY table_name;
            """))
            
            new_tables = [row[0] for row in result.fetchall()]
            logger.info(f"✅ New architecture tables available: {new_tables}")
            
            # Check for old tables that might need migration
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name NOT IN ('ideas', 'refinement_sessions', 'plans')
                ORDER BY table_name;
            """))
            
            old_tables = [row[0] for row in result.fetchall()]
            if old_tables:
                logger.info(f"⚠️  Existing tables found: {old_tables}")
                logger.info("These tables contain old data that may need manual migration")
        
        logger.info("✅ Database migration completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Update your application to use main_new.py")
        logger.info("2. Verify that OpenAI API key is set in environment")
        logger.info("3. Test the new API endpoints")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

def show_migration_info():
    """Show information about the migration"""
    print("\n" + "="*60)
    print("BRIGHT IDEAS - NEW ARCHITECTURE MIGRATION")
    print("="*60)
    print("\nThis migration will:")
    print("✓ Create new tables: ideas, refinement_sessions, plans")
    print("✓ Support AI-generated refinement questions")
    print("✓ Enable structured plan generation and export")
    print("✓ Maintain data integrity with proper relationships")
    print("\nRequired environment variables:")
    print("- DATABASE_URL: PostgreSQL connection string")
    print("- OPENAI_API_KEY: Your OpenAI API key")
    print("- OPENAI_MODEL: Model to use (default: gpt-4o)")
    print("\nNew API workflow:")
    print("1. POST /api/v1/ideas/ - Create idea")
    print("2. POST /api/v1/refinement/sessions/ - Start refinement")
    print("3. PUT /api/v1/refinement/sessions/{id}/answers/ - Submit answers")
    print("4. POST /api/v1/plans/generate/ - Generate plan")
    print("5. GET /api/v1/plans/{id}/export/json - Export plan")
    print("\n" + "="*60)

if __name__ == "__main__":
    show_migration_info()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        logger.info(f"Using database: {settings.database_url}")
        logger.info(f"Environment: {settings.environment}")
        migrate_database()
    else:
        print("\nTo run the migration, use: python migrate_to_new_architecture.py --run")
        print("⚠️  Make sure to backup your existing database first!")