import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database.models import Base
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.Session = None
    
    def init_db(self):
        """Initialize database connection"""
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'telegram_bot')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        
        logger.info(f"Connecting to database at {db_host}:{db_port}/{db_name}")
        
        self.engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
        
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")
    
    def get_session(self):
        """Get database session"""
        return self.Session()
    
    def close(self):
        """Close database connection"""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()


# Global database instance
db = Database()