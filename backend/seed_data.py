#!/usr/bin/env python3
"""
Database seeding script for Personal Finance App
Populates the database with sample categories, transactions, and investments
"""

from app import create_app
from models import db, Category, Transaction, Investment
from datetime import date, timedelta
import random

def seed_database():
    """Seed the database with sample data"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Seeding categories...")
        # Create sample categories
        categories = [
            Category(name='Salary', type='income', color='#10B981'),
            Category(name='Freelance', type='income', color='#3B82F6'),
            Category(name='Food & Dining', type='expense', color='#EF4444', budget_limit=400.0),
            Category(name='Transportation', type='expense', color='#F59E0B', budget_limit=200.0),
            Category(name='Housing', type='expense', color='#8B5CF6', budget_limit=1200.0),
            Category(name='Entertainment', type='expense', color='#EC4899', budget_limit=150.0),
            Category(name='Healthcare', type='expense', color='#06B6D4', budget_limit=100.0),
            Category(name='Shopping', type='expense', color='#84CC16', budget_limit=300.0),
            Category(name='Utilities', type='expense', color='#F97316', budget_limit=250.0),
            Category(name='Investment Returns', type='income', color='#22C55E'),
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        print(f"Created {len(categories)} categories")
        
        print("Seeding transactions...")
        # Create sample transactions for the last 3 months
        transactions = []
        today = date.today()
        
        # Income transactions
        for i in range(3):
            # Monthly salary
            salary_date = today - timedelta(days=30*i)
            transactions.append(Transaction(
                date=salary_date,
                amount=3500.00,
                category_id=categories[0].id,  # Salary
                description='Monthly Salary',
                type='income'
            ))
            
            # Freelance income (random)
            if random.random() > 0.5:
                freelance_date = salary_date + timedelta(days=random.randint(5, 25))
                transactions.append(Transaction(
                    date=freelance_date,
                    amount=random.randint(200, 800),
                    category_id=categories[1].id,  # Freelance
                    description='Freelance Project',
                    type='income'
                ))
        
        # Expense transactions
        expense_categories = [cat for cat in categories if cat.type == 'expense']
        
        for i in range(90):  # Last 90 days
            transaction_date = today - timedelta(days=i)
            if random.random() > 0.3:  # 70% chance of having an expense each day
                category = random.choice(expense_categories)
                amount = 0
                
                if category.name == 'Food & Dining':
                    amount = random.randint(15, 80)
                elif category.name == 'Transportation':
                    amount = random.randint(10, 50)
                elif category.name == 'Housing':
                    amount = 1200 if i % 30 == 0 else 0  # Monthly rent
                elif category.name == 'Entertainment':
                    amount = random.randint(20, 120) if random.random() > 0.7 else 0
                elif category.name == 'Healthcare':
                    amount = random.randint(25, 150) if random.random() > 0.8 else 0
                elif category.name == 'Shopping':
                    amount = random.randint(30, 200) if random.random() > 0.6 else 0
                elif category.name == 'Utilities':
                    amount = random.randint(80, 180) if i % 30 == 0 else 0  # Monthly utilities
                
                if amount > 0:
                    transactions.append(Transaction(
                        date=transaction_date,
                        amount=-amount,  # Negative for expenses
                        category_id=category.id,
                        description=f'{category.name} expense',
                        type='expense'
                    ))
        
        # Add some investment returns
        for i in range(3):
            return_date = today - timedelta(days=30*i + random.randint(10, 25))
            transactions.append(Transaction(
                date=return_date,
                amount=random.randint(50, 300),
                category_id=categories[9].id,  # Investment Returns
                description='Investment Dividend',
                type='income'
            ))
        
        for transaction in transactions:
            db.session.add(transaction)
        
        db.session.commit()
        print(f"Created {len(transactions)} transactions")
        
        print("Seeding investments...")
        # Create sample investments
        investments = [
            Investment(
                asset_name='AAPL',
                asset_type='stock',
                quantity=10.0,
                purchase_price=150.0,
                current_price=175.0,
                purchase_date=date(2023, 1, 15)
            ),
            Investment(
                asset_name='GOOGL',
                asset_type='stock',
                quantity=5.0,
                purchase_price=120.0,
                current_price=135.0,
                purchase_date=date(2023, 3, 20)
            ),
            Investment(
                asset_name='ETH',
                asset_type='crypto',
                quantity=2.5,
                purchase_price=1800.0,
                current_price=2200.0,
                purchase_date=date(2023, 6, 10)
            ),
            Investment(
                asset_name='VTI',
                asset_type='etf',
                quantity=25.0,
                purchase_price=200.0,
                current_price=215.0,
                purchase_date=date(2023, 2, 5)
            ),
            Investment(
                asset_name='TSLA',
                asset_type='stock',
                quantity=8.0,
                purchase_price=250.0,
                current_price=220.0,
                purchase_date=date(2023, 4, 12)
            ),
        ]
        
        for investment in investments:
            db.session.add(investment)
        
        db.session.commit()
        print(f"Created {len(investments)} investments")
        
        print("\nDatabase seeding completed successfully!")
        print(f"Categories: {len(categories)}")
        print(f"Transactions: {len(transactions)}")
        print(f"Investments: {len(investments)}")
        
        # Print some sample data
        print("\nSample data preview:")
        print("Categories:")
        for cat in categories[:5]:
            print(f"  - {cat.name} ({cat.type}) - Budget: {cat.budget_limit or 'None'}")
        
        print("\nRecent transactions:")
        recent_txs = Transaction.query.order_by(Transaction.date.desc()).limit(5).all()
        for tx in recent_txs:
            print(f"  - {tx.date}: {tx.description} - ${tx.amount} ({tx.type})")
        
        print("\nInvestments:")
        for inv in investments:
            print(f"  - {inv.asset_name}: {inv.quantity} @ ${inv.current_price} (Gain: ${inv.total_gain_loss:.2f})")

if __name__ == '__main__':
    seed_database()
