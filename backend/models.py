"""
Database models for Personal Finance App
Defines SQLAlchemy models for categories, transactions, and investments
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy.ext.hybrid import hybrid_property
import json

db = SQLAlchemy()

class Category(db.Model):
    """Budget category model (income/expense categories)"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    color = db.Column(db.String(7), nullable=False, default='#007bff')  # Hex color
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy=True)
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Category {self.name} ({self.type})>'

class Transaction(db.Model):
    """Financial transaction model"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @hybrid_property
    def is_income(self):
        """Check if transaction is income"""
        return self.type == 'income'
    
    @hybrid_property
    def is_expense(self):
        """Check if transaction is expense"""
        return self.type == 'expense'
    
    @hybrid_property
    def absolute_amount(self):
        """Get absolute value of amount"""
        return abs(float(self.amount))
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'amount': float(self.amount),
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'category_color': self.category.color if self.category else None,
            'description': self.description,
            'type': self.type,
            'is_income': self.is_income,
            'is_expense': self.is_expense,
            'absolute_amount': self.absolute_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Transaction {self.description} ({self.amount}) on {self.date}>'

class Investment(db.Model):
    """Investment holding model"""
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(100), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)  # 'stock', 'crypto', 'bond', etc.
    quantity = db.Column(db.Numeric(15, 6), nullable=False)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    current_price = db.Column(db.Numeric(10, 2), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @hybrid_property
    def total_invested(self):
        """Calculate total amount invested"""
        return float(self.quantity) * float(self.purchase_price)
    
    @hybrid_property
    def current_value(self):
        """Calculate current total value"""
        return float(self.quantity) * float(self.current_price)
    
    @hybrid_property
    def total_gain_loss(self):
        """Calculate total gain/loss"""
        return self.current_value - self.total_invested
    
    @hybrid_property
    def gain_loss_percentage(self):
        """Calculate gain/loss percentage"""
        if self.total_invested == 0:
            return 0
        return (self.total_gain_loss / self.total_invested) * 100
    
    @hybrid_property
    def is_profitable(self):
        """Check if investment is profitable"""
        return self.total_gain_loss > 0
    
    def update_current_price(self, new_price):
        """Update current price and recalculate values"""
        self.current_price = new_price
        self.updated_at = datetime.utcnow()
        return self
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'asset_name': self.asset_name,
            'asset_type': self.asset_type,
            'quantity': float(self.quantity),
            'purchase_price': float(self.purchase_price),
            'current_price': float(self.current_price),
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'total_invested': self.total_invested,
            'current_value': self.current_value,
            'total_gain_loss': self.total_gain_loss,
            'gain_loss_percentage': self.gain_loss_percentage,
            'is_profitable': self.is_profitable,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Investment {self.asset_name} ({self.quantity} @ ${self.current_price})>'

# Utility functions for common operations
def get_total_income(start_date=None, end_date=None):
    """Get total income for a date range"""
    query = Transaction.query.filter_by(type='income')
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    result = query.with_entities(db.func.sum(Transaction.amount)).scalar()
    return float(result) if result else 0.0

def get_total_expenses(start_date=None, end_date=None):
    """Get total expenses for a date range"""
    query = Transaction.query.filter_by(type='expense')
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    result = query.with_entities(db.func.sum(Transaction.amount)).scalar()
    return abs(float(result)) if result else 0.0

def get_net_income(start_date=None, end_date=None):
    """Get net income (income - expenses) for a date range"""
    income = get_total_income(start_date, end_date)
    expenses = get_total_expenses(start_date, end_date)
    return income - expenses

def get_total_investment_value():
    """Get total current value of all investments"""
    result = Investment.query.with_entities(db.func.sum(Investment.current_value)).scalar()
    return float(result) if result else 0.0

def get_total_investment_gain_loss():
    """Get total gain/loss across all investments"""
    result = Investment.query.with_entities(db.func.sum(Investment.total_gain_loss)).scalar()
    return float(result) if result else 0.0

def update_investment_prices():
    """
    Placeholder function for updating investment prices
    CUSTOMIZATION POINT: Implement your own price update logic here
    
    This could include:
    - API calls to financial data providers
    - Web scraping from financial websites
    - Integration with trading platforms
    - Real-time price feeds
    """
    print("Investment price update function called - customize this for your needs!")
    
    # Example implementation structure:
    # for investment in Investment.query.all():
    #     if investment.asset_type == 'stock':
    #         new_price = get_stock_price(investment.asset_name)
    #     elif investment.asset_type == 'crypto':
    #         new_price = get_crypto_price(investment.asset_name)
    #     else:
    #         new_price = get_other_asset_price(investment.asset_name)
    #     
    #     investment.update_current_price(new_price)
    # 
    # db.session.commit()
    
    return True
