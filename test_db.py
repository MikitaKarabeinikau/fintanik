from dotenv import load_dotenv
load_dotenv()  # Load .env first

from database.db import db
from database.models import Transaction, User

# Test connection
try:
    db.init_db()
    print("✓ Database initialized successfully")
    
    session = db.get_session()
    user_count = session.query(User).count()
    trans_count = session.query(Transaction).count()
    
    print(f"✓ Users in database: {user_count}")
    print(f"✓ Transactions in database: {trans_count}")
    
    session.close()
        
except Exception as e:
    print(f"✗ Database connection failed: {e}")
    exit(1)
