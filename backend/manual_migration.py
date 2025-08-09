"""
Manual migration script to handle database schema updates
"""
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
import logging
from config import settings

logger = logging.getLogger(__name__)

def apply_manual_migrations():
    """Apply manual migrations for schema updates"""
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        try:
            # Check if is_unrefined column exists, if not add it
            try:
                conn.execute(text("SELECT is_unrefined FROM ideas LIMIT 1"))
                logger.info("is_unrefined column already exists")
            except (OperationalError, ProgrammingError):
                logger.info("Adding is_unrefined column to ideas table")
                conn.execute(text("ALTER TABLE ideas ADD COLUMN is_unrefined BOOLEAN DEFAULT FALSE"))
                conn.commit()
                
            # Check if todos table exists, if not create it
            try:
                conn.execute(text("SELECT COUNT(*) FROM todos"))
                logger.info("todos table already exists")
            except (OperationalError, ProgrammingError):
                logger.info("Creating todos table")
                conn.execute(text("""
                    CREATE TABLE todos (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        text TEXT NOT NULL,
                        is_completed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
                
            logger.info("Manual migrations completed successfully")
            
        except Exception as e:
            logger.error(f"Manual migration failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    apply_manual_migrations()