"""
Shared test configuration and fixtures for Personal Finance App tests
"""

import pytest
import sys
import os
from datetime import datetime, date, timedelta

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, Category, Transaction
from routes import api


@pytest.fixture
def app():
    """Create and configure a test app instance"""
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    test_app.register_blueprint(api)

    # Initialize database
    db.init_app(test_app)

    return test_app


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture
def init_database(app):
    """Initialize database with test data"""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture
def sample_categories(init_database):
    """Create sample categories for testing"""
    categories = [
        Category(name='Groceries', type='expense', color='#FF6B6B',
                budget_limit=500.0, budget_period='monthly', budget_type='fixed'),
        Category(name='Entertainment', type='expense', color='#4ECDC4',
                budget_limit=200.0, budget_period='monthly', budget_type='fixed'),
        Category(name='Transportation', type='expense', color='#45B7D1',
                budget_limit=300.0, budget_period='monthly', budget_type='fixed'),
        Category(name='Utilities', type='expense', color='#96CEB4',
                budget_limit=400.0, budget_period='monthly', budget_type='fixed'),
        Category(name='Salary', type='income', color='#2ECC71'),
    ]

    for category in categories:
        db.session.add(category)
    db.session.commit()

    return categories


@pytest.fixture
def sample_transactions(sample_categories):
    """Create sample transactions for testing"""
    current_date = date.today()
    start_of_month = date(current_date.year, current_date.month, 1)

    # Get category IDs
    groceries = next(cat for cat in sample_categories if cat.name == 'Groceries')
    entertainment = next(cat for cat in sample_categories if cat.name == 'Entertainment')
    transportation = next(cat for cat in sample_categories if cat.name == 'Transportation')
    utilities = next(cat for cat in sample_categories if cat.name == 'Utilities')
    salary = next(cat for cat in sample_categories if cat.name == 'Salary')

    transactions = [
        # Income
        Transaction(date=start_of_month, amount=3000.0, category_id=salary.id,
                   description='Monthly salary', type='income'),

        # Expenses
        Transaction(date=start_of_month + timedelta(days=5), amount=-120.0,
                   category_id=groceries.id, description='Weekly groceries', type='expense'),
        Transaction(date=start_of_month + timedelta(days=12), amount=-80.0,
                   category_id=entertainment.id, description='Movie night', type='expense'),
        Transaction(date=start_of_month + timedelta(days=8), amount=-60.0,
                   category_id=transportation.id, description='Gas', type='expense'),
        Transaction(date=start_of_month + timedelta(days=10), amount=-100.0,
                   category_id=utilities.id, description='Electricity', type='expense'),
    ]

    for transaction in transactions:
        db.session.add(transaction)
    db.session.commit()

    return transactions


@pytest.fixture
def current_month():
    """Get current month date range"""
    current_date = date.today()
    start_of_month = date(current_date.year, current_date.month, 1)
    if current_date.month == 12:
        end_of_month = date(current_date.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(current_date.year, current_date.month + 1, 1) - timedelta(days=1)

    return start_of_month, end_of_month
