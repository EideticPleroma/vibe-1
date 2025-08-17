"""
Database initialization script for Personal Finance App
Creates SQLite database and initializes tables with sample data
"""

from models import db, Category, Transaction, Investment
from datetime import datetime, date
import os

def init_db():
    """Initialize the database and create tables"""
    
    # Create database directory if it doesn't exist
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Create all tables
    db.create_all()
    
    # Check if categories already exist to avoid duplicates
    if Category.query.first() is None:
        create_sample_categories()
    
    if Transaction.query.first() is None:
        create_sample_transactions()
    
    if Investment.query.first() is None:
        create_sample_investments()
    
    print("Database initialized successfully!")

def create_sample_categories():
    """Create sample budget categories"""
    categories = [
        Category(name="Salary", type="income", color="#28a745"),
        Category(name="Freelance", type="income", color="#17a2b8"),
        Category(name="Investment Returns", type="income", color="#ffc107"),
        Category(name="Groceries", type="expense", color="#dc3545"),
        Category(name="Transportation", type="expense", color="#fd7e14"),
        Category(name="Entertainment", type="expense", color="#e83e8c"),
        Category(name="Utilities", type="expense", color="#6f42c1"),
        Category(name="Healthcare", type="expense", color="#20c997"),
        Category(name="Shopping", type="expense", color="#6c757d"),
        Category(name="Dining Out", type="expense", color="#fd7e14")
    ]
    
    for category in categories:
        db.session.add(category)
    
    db.session.commit()
    print("Sample categories created!")

def create_sample_transactions():
    """Create sample transactions"""
    # Get category IDs
    salary_cat = Category.query.filter_by(name="Salary").first()
    groceries_cat = Category.query.filter_by(name="Groceries").first()
    transport_cat = Category.query.filter_by(name="Transportation").first()
    
    transactions = [
        Transaction(
            date=date(2024, 1, 15),
            amount=5000.00,
            category_id=salary_cat.id,
            description="Monthly salary",
            type="income"
        ),
        Transaction(
            date=date(2024, 1, 16),
            amount=-120.50,
            category_id=groceries_cat.id,
            description="Weekly groceries",
            type="expense"
        ),
        Transaction(
            date=date(2024, 1, 17),
            amount=-45.00,
            category_id=transport_cat.id,
            description="Gas and parking",
            type="expense"
        ),
        Transaction(
            date=date(2024, 1, 18),
            amount=-85.00,
            category_id=groceries_cat.id,
            description="Restaurant dinner",
            type="expense"
        )
    ]
    
    for transaction in transactions:
        db.session.add(transaction)
    
    db.session.commit()
    print("Sample transactions created!")

def create_sample_investments():
    """Create sample investment holdings"""
    investments = [
        Investment(
            asset_name="AAPL",
            asset_type="stock",
            quantity=10,
            purchase_price=150.00,
            current_price=175.50,
            purchase_date=date(2023, 6, 15)
        ),
        Investment(
            asset_name="TSLA",
            asset_type="stock",
            quantity=5,
            purchase_price=200.00,
            current_price=250.00,
            purchase_date=date(2023, 8, 20)
        ),
        Investment(
            asset_name="Bitcoin",
            asset_type="crypto",
            quantity=0.5,
            purchase_price=45000.00,
            current_price=52000.00,
            purchase_date=date(2023, 5, 10)
        ),
        Investment(
            asset_name="Ethereum",
            asset_type="crypto",
            quantity=2.0,
            purchase_price=2800.00,
            current_price=3200.00,
            purchase_date=date(2023, 7, 12)
        )
    ]
    
    for investment in investments:
        db.session.add(investment)
    
    db.session.commit()
    print("Sample investments created!")

if __name__ == "__main__":
    # Import app context to initialize database
    from app import app
    with app.app_context():
        init_db()
