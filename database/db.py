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

        logger.info(f"DB_NAME from env: {os.getenv('DB_NAME')}")
        logger.info(f"DB_USER from env: {os.getenv('DB_USER')}")
        
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
        self._seed_terms()
    
    def get_session(self):
        """Get database session"""
        session = self.Session()
        if not session.is_active:
            session.rollback()
        return session
    
    def close(self):
        """Close database connection"""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()

    def _seed_terms(self):
        """Seed terms table with default values"""
        from database.models import Terms
        session = self.get_session()
        try:
            if session.query(Terms).count() >0:
                logger.info("Terms table already seeded")
                return
            
            terms_data = [
                Terms(id=0, weekday='Monday', start_time=None, end_time=None),
                Terms(id=1, weekday='Tuesday', start_time=None, end_time=None),
                Terms(id=2, weekday='Wednesday', start_time=None, end_time=None),
                Terms(id=3, weekday='Thursday', start_time=None, end_time=None),
                Terms(id=4, weekday='Friday', start_time=None, end_time=None),
                Terms(id=5, weekday='Saturday', start_time=None, end_time=None),
                Terms(id=6, weekday='Sunday', start_time=None, end_time=None),
            ]

            session.bulk_save_objects(terms_data)
            session.commit()
            logger.info("Seeded terms table with default values")
        except Exception as e:
            session.rollback()
            logger.error(f"Error seeding terms table: {e}")
        finally:
            session.close()

# Global database instance
db = Database()