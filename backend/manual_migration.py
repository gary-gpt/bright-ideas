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
    
    with engine.begin() as conn:  # Use begin() for transaction management
        try:
            # Check if is_unrefined column exists, if not add it
            try:
                result = conn.execute(text("SELECT is_unrefined FROM ideas LIMIT 1"))
                logger.info("is_unrefined column already exists")
            except (OperationalError, ProgrammingError) as e:
                logger.info(f"Adding is_unrefined column to ideas table (error: {e})")
                try:
                    conn.execute(text("ALTER TABLE ideas ADD COLUMN is_unrefined BOOLEAN DEFAULT FALSE"))
                    logger.info("Successfully added is_unrefined column")
                except Exception as alter_error:
                    logger.error(f"Failed to add is_unrefined column: {alter_error}")
                    # Continue with other migrations even if this fails
                
            # Check if todos table exists, if not create it
            try:
                conn.execute(text("SELECT COUNT(*) FROM todos"))
                logger.info("todos table already exists")
            except (OperationalError, ProgrammingError) as e:
                logger.info(f"Creating todos table (error: {e})")
                try:
                    conn.execute(text("""
                        CREATE TABLE todos (
                            id UUID PRIMARY KEY,
                            text TEXT NOT NULL,
                            is_completed BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    logger.info("Successfully created todos table")
                except Exception as create_error:
                    logger.error(f"Failed to create todos table: {create_error}")
                
            logger.info("Manual migrations completed successfully")
            
        except Exception as e:
            logger.error(f"Manual migration failed: {e}")
            raise

if __name__ == "__main__":
    apply_manual_migrations()