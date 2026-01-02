"""Database configuration and session management."""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# SQLite database path (in project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = BASE_DIR / "smartsupport.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite - allows multi-threaded access
    echo=False  # Set to True for SQL query logging
)

# Enable WAL (Write-Ahead Logging) mode for SQLite
# This allows concurrent reads/writes and fixes "readonly database" errors
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable WAL mode on SQLite connection to allow concurrent access."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()
    logger.debug("SQLite WAL mode enabled")

# Log database connection
logger.info(f"Database connected at: {DATABASE_URL}")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and closes it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database by creating all tables and migrating existing ones."""
    from app.models.sql_models import Ticket  # Import to register models
    from sqlalchemy import text
    
    Base.metadata.create_all(bind=engine)
    
    # Migrate existing tables: Add new columns if they don't exist
    # This handles existing databases that were created before columns were added
    try:
        with engine.begin() as conn:  # begin() handles transaction automatically
            # Check and add sanitized_text column if it doesn't exist
            result = conn.execute(
                text("SELECT name FROM pragma_table_info('tickets') WHERE name='sanitized_text'")
            )
            if not result.fetchone():
                logger.info("Adding sanitized_text column to tickets table...")
                conn.execute(text("ALTER TABLE tickets ADD COLUMN sanitized_text TEXT"))
                logger.info("✅ sanitized_text column added successfully")
            else:
                logger.debug("sanitized_text column already exists")
            
            # Check and add prediction_details column if it doesn't exist
            result = conn.execute(
                text("SELECT name FROM pragma_table_info('tickets') WHERE name='prediction_details'")
            )
            if not result.fetchone():
                logger.info("Adding prediction_details column to tickets table...")
                conn.execute(text("ALTER TABLE tickets ADD COLUMN prediction_details TEXT"))
                logger.info("✅ prediction_details column added successfully")
            else:
                logger.debug("prediction_details column already exists")
    except Exception as e:
        logger.warning(f"Could not migrate columns (may already exist): {str(e)}")

