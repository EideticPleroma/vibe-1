#!/usr/bin/env python3
"""
Comprehensive data seeding script for Personal Finance App
Seeds realistic financial data for demonstrating budget methodology features
"""

import sys
import os
from datetime import date, timedelta, datetime
from decimal import Decimal
import random

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Category, Transaction, Investment, BudgetMethodology

def clear_existing_data():
    """Clear existing data (except methodologies) for fresh seeding"""
    print("Clearing existing data...")
    
    with app.app_context():
        # Keep methodologies but clear other data
        Transaction.query.delete()
        Investment.query.delete()
        Category.query.delete()
        
        db.session.commit()
        print("✓ Existing data cleared")

def seed_categories():
    """Seed realistic categories with budget settings"""
    print("Seeding categories...")
    
    with app.app_context():
        categories_data = [
            # Income Categories
            {
                'name': 'Salary',
                'type': 'income',
                'color': '#10B981'
            },
            {
                'name': 'Freelance',
                'type': 'income',
                'color': '#34D399'
            },
            {
                'name': 'Investment Returns',
                'type': 'income',
                'color': '#6EE7B7'
            },
            
            # Critical Expense Categories
            {
                'name': 'Rent/Mortgage',
                'type': 'expense',
                'color': '#EF4444',
                'budget_limit': 1800.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'critical'
            },
            {
                'name': 'Utilities',
                'type': 'expense',
                'color': '#F97316',
                'budget_limit': 250.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'critical'
            },
            {
                'name': 'Insurance',
                'type': 'expense',
                'color': '#DC2626',
                'budget_limit': 180.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'critical'
            },
            
            # Essential Expense Categories
            {
                'name': 'Groceries',
                'type': 'expense',
                'color': '#059669',
                'budget_limit': 600.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'essential'
            },
            {
                'name': 'Transportation',
                'type': 'expense',
                'color': '#0891B2',
                'budget_limit': 320.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'essential'
            },
            {
                'name': 'Healthcare',
                'type': 'expense',
                'color': '#7C3AED',
                'budget_limit': 150.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'essential'
            },
            {
                'name': 'Phone & Internet',
                'type': 'expense',
                'color': '#2563EB',
                'budget_limit': 120.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'essential'
            },
            
            # Important Expense Categories
            {
                'name': 'Dining Out',
                'type': 'expense',
                'color': '#F59E0B',
                'budget_limit': 300.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'important'
            },
            {
                'name': 'Shopping',
                'type': 'expense',
                'color': '#EC4899',
                'budget_limit': 250.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'important'
            },
            {
                'name': 'Gym & Fitness',
                'type': 'expense',
                'color': '#8B5CF6',
                'budget_limit': 80.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'important'
            },
            {
                'name': 'Personal Care',
                'type': 'expense',
                'color': '#F472B6',
                'budget_limit': 100.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'important'
            },
            
            # Discretionary Expense Categories
            {
                'name': 'Entertainment',
                'type': 'expense',
                'color': '#06B6D4',
                'budget_limit': 200.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'discretionary'
            },
            {
                'name': 'Subscriptions',
                'type': 'expense',
                'color': '#84CC16',
                'budget_limit': 85.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'discretionary'
            },
            {
                'name': 'Travel',
                'type': 'expense',
                'color': '#F97316',
                'budget_limit': 400.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'discretionary'
            },
            {
                'name': 'Gifts & Donations',
                'type': 'expense',
                'color': '#EF4444',
                'budget_limit': 150.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'discretionary'
            },
            {
                'name': 'Hobbies',
                'type': 'expense',
                'color': '#8B5CF6',
                'budget_limit': 120.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'discretionary'
            },
            {
                'name': 'Miscellaneous',
                'type': 'expense',
                'color': '#6B7280',
                'budget_limit': 100.00,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'discretionary'
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category(
                name=cat_data['name'],
                type=cat_data['type'],
                color=cat_data['color'],
                budget_limit=cat_data.get('budget_limit'),
                budget_period=cat_data.get('budget_period', 'monthly'),
                budget_type=cat_data.get('budget_type', 'fixed'),
                budget_priority=cat_data.get('budget_priority', 'essential')
            )
            categories.append(category)
            db.session.add(category)
        
        db.session.commit()
        print(f"✓ Created {len(categories)} categories")
        return categories

def seed_transactions():
    """Seed realistic transactions for the past 3 months"""
    print("Seeding transactions...")
    
    with app.app_context():
        categories = Category.query.all()
        income_categories = [c for c in categories if c.type == 'income']
        expense_categories = [c for c in categories if c.type == 'expense']
        
        transactions = []
        
        # Generate transactions for the past 3 months
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        current_date = start_date
        
        while current_date <= end_date:
            # Add salary income (monthly, around the 1st)
            if current_date.day == 1:
                salary_category = next((c for c in income_categories if c.name == 'Salary'), None)
                if salary_category:
                    # Salary between $4,800 - $5,200
                    salary_amount = random.uniform(4800, 5200)
                    transaction = Transaction(
                        date=current_date,
                        amount=round(salary_amount, 2),
                        category_id=salary_category.id,
                        description='Monthly Salary',
                        type='income'
                    )
                    transactions.append(transaction)
            
            # Add freelance income occasionally
            if random.random() < 0.15:  # 15% chance per day
                freelance_category = next((c for c in income_categories if c.name == 'Freelance'), None)
                if freelance_category:
                    freelance_amount = random.uniform(200, 800)
                    transaction = Transaction(
                        date=current_date,
                        amount=round(freelance_amount, 2),
                        category_id=freelance_category.id,
                        description='Freelance Project',
                        type='income'
                    )
                    transactions.append(transaction)
            
            # Add regular expenses based on category
            for expense_cat in expense_categories:
                # Define probability and amount ranges based on category
                expense_patterns = {
                    'Rent/Mortgage': {'prob': 0.03, 'min': 1750, 'max': 1850, 'desc': ['Monthly Rent', 'Mortgage Payment']},
                    'Utilities': {'prob': 0.05, 'min': 50, 'max': 120, 'desc': ['Electric Bill', 'Gas Bill', 'Water Bill']},
                    'Insurance': {'prob': 0.02, 'min': 150, 'max': 200, 'desc': ['Health Insurance', 'Car Insurance', 'Life Insurance']},
                    'Groceries': {'prob': 0.25, 'min': 30, 'max': 150, 'desc': ['Grocery Store', 'Supermarket', 'Organic Market']},
                    'Transportation': {'prob': 0.15, 'min': 3, 'max': 45, 'desc': ['Gas Station', 'Public Transit', 'Uber', 'Parking']},
                    'Healthcare': {'prob': 0.08, 'min': 25, 'max': 200, 'desc': ['Doctor Visit', 'Pharmacy', 'Dental Care']},
                    'Phone & Internet': {'prob': 0.03, 'min': 100, 'max': 140, 'desc': ['Phone Bill', 'Internet Bill']},
                    'Dining Out': {'prob': 0.20, 'min': 15, 'max': 80, 'desc': ['Restaurant', 'Coffee Shop', 'Fast Food', 'Food Delivery']},
                    'Shopping': {'prob': 0.12, 'min': 20, 'max': 150, 'desc': ['Clothing Store', 'Online Shopping', 'Department Store']},
                    'Gym & Fitness': {'prob': 0.04, 'min': 70, 'max': 90, 'desc': ['Gym Membership', 'Fitness Class']},
                    'Personal Care': {'prob': 0.08, 'min': 15, 'max': 60, 'desc': ['Haircut', 'Pharmacy', 'Beauty Products']},
                    'Entertainment': {'prob': 0.10, 'min': 12, 'max': 60, 'desc': ['Movie Theater', 'Concert', 'Streaming Service', 'Games']},
                    'Subscriptions': {'prob': 0.03, 'min': 8, 'max': 25, 'desc': ['Netflix', 'Spotify', 'Software Subscription']},
                    'Travel': {'prob': 0.03, 'min': 100, 'max': 600, 'desc': ['Flight Ticket', 'Hotel', 'Car Rental']},
                    'Gifts & Donations': {'prob': 0.05, 'min': 20, 'max': 100, 'desc': ['Gift', 'Charity Donation', 'Birthday Present']},
                    'Hobbies': {'prob': 0.06, 'min': 15, 'max': 80, 'desc': ['Art Supplies', 'Books', 'Hobby Equipment']},
                    'Miscellaneous': {'prob': 0.08, 'min': 10, 'max': 50, 'desc': ['Miscellaneous', 'Other Expense']}
                }
                
                pattern = expense_patterns.get(expense_cat.name, {'prob': 0.05, 'min': 10, 'max': 50, 'desc': ['Expense']})
                
                if random.random() < pattern['prob']:
                    amount = random.uniform(pattern['min'], pattern['max'])
                    description = random.choice(pattern['desc'])
                    
                    transaction = Transaction(
                        date=current_date,
                        amount=-round(amount, 2),  # Negative for expenses
                        category_id=expense_cat.id,
                        description=description,
                        type='expense'
                    )
                    transactions.append(transaction)
            
            current_date += timedelta(days=1)
        
        # Add all transactions to database
        for transaction in transactions:
            db.session.add(transaction)
        
        db.session.commit()
        print(f"✓ Created {len(transactions)} transactions")
        return transactions

def seed_investments():
    """Seed sample investment portfolio"""
    print("Seeding investments...")
    
    with app.app_context():
        investments_data = [
            {
                'asset_name': 'Apple Inc. (AAPL)',
                'asset_type': 'stock',
                'quantity': 25,
                'purchase_price': 150.25,
                'current_price': 185.30,
                'purchase_date': date.today() - timedelta(days=120)
            },
            {
                'asset_name': 'Microsoft Corporation (MSFT)',
                'asset_type': 'stock',
                'quantity': 15,
                'purchase_price': 280.50,
                'current_price': 295.75,
                'purchase_date': date.today() - timedelta(days=90)
            },
            {
                'asset_name': 'Vanguard S&P 500 ETF (VOO)',
                'asset_type': 'etf',
                'quantity': 50,
                'purchase_price': 380.00,
                'current_price': 405.20,
                'purchase_date': date.today() - timedelta(days=180)
            },
            {
                'asset_name': 'Bitcoin (BTC)',
                'asset_type': 'crypto',
                'quantity': 0.5,
                'purchase_price': 35000.00,
                'current_price': 42500.00,
                'purchase_date': date.today() - timedelta(days=60)
            },
            {
                'asset_name': 'Tesla Inc. (TSLA)',
                'asset_type': 'stock',
                'quantity': 10,
                'purchase_price': 220.80,
                'current_price': 195.45,
                'purchase_date': date.today() - timedelta(days=45)
            },
            {
                'asset_name': 'Vanguard Total Bond Market ETF (BND)',
                'asset_type': 'bond',
                'quantity': 30,
                'purchase_price': 85.50,
                'current_price': 83.25,
                'purchase_date': date.today() - timedelta(days=200)
            }
        ]
        
        investments = []
        for inv_data in investments_data:
            investment = Investment(
                asset_name=inv_data['asset_name'],
                asset_type=inv_data['asset_type'],
                quantity=inv_data['quantity'],
                purchase_price=inv_data['purchase_price'],
                current_price=inv_data['current_price'],
                purchase_date=inv_data['purchase_date']
            )
            investments.append(investment)
            db.session.add(investment)
        
        db.session.commit()
        print(f"✓ Created {len(investments)} investments")
        return investments

def display_summary():
    """Display a summary of seeded data"""
    print("\n" + "="*50)
    print("DATA SEEDING SUMMARY")
    print("="*50)
    
    with app.app_context():
        # Categories summary
        income_cats = Category.query.filter_by(type='income').count()
        expense_cats = Category.query.filter_by(type='expense').count()
        print(f"📊 Categories: {income_cats} income, {expense_cats} expense")
        
        # Transactions summary
        income_trans = Transaction.query.filter_by(type='income').count()
        expense_trans = Transaction.query.filter_by(type='expense').count()
        print(f"💰 Transactions: {income_trans} income, {expense_trans} expense")
        
        # Financial summary (last 30 days)
        from models import get_total_income, get_total_expenses, get_net_income
        from datetime import date, timedelta
        
        last_30_days = date.today() - timedelta(days=30)
        monthly_income = get_total_income(last_30_days, date.today())
        monthly_expenses = get_total_expenses(last_30_days, date.today())
        monthly_net = get_net_income(last_30_days, date.today())
        
        print(f"📈 Last 30 Days Financial Summary:")
        print(f"   • Income: ${monthly_income:,.2f}")
        print(f"   • Expenses: ${monthly_expenses:,.2f}")
        print(f"   • Net Income: ${monthly_net:,.2f}")
        print(f"   • Savings Rate: {(monthly_net/monthly_income*100):.1f}%" if monthly_income > 0 else "   • Savings Rate: N/A")
        
        # Investment summary
        from models import get_total_investment_value, get_total_investment_gain_loss
        total_value = get_total_investment_value()
        total_gain_loss = get_total_investment_gain_loss()
        
        print(f"🏦 Investment Portfolio:")
        print(f"   • Total Value: ${total_value:,.2f}")
        print(f"   • Total Gain/Loss: ${total_gain_loss:,.2f}")
        print(f"   • Return: {(total_gain_loss/total_value*100):.1f}%" if total_value > 0 else "   • Return: N/A")
        
        # Budget methodology summary
        methodologies = BudgetMethodology.query.count()
        active_methodology = BudgetMethodology.query.filter_by(is_active=True).first()
        print(f"🎯 Budget Methodologies: {methodologies} available")
        if active_methodology:
            print(f"   • Active: {active_methodology.name}")
        
        print("\n✅ Database seeding completed successfully!")
        print("🚀 Your finance app is now ready with realistic data for testing!")

def main():
    """Main seeding function"""
    print("🌱 COMPREHENSIVE DATA SEEDING FOR PERSONAL FINANCE APP")
    print("This will populate your database with realistic financial data.")
    print()
    
    try:
        # Clear existing data (except methodologies)
        clear_existing_data()
        
        # Seed data in order
        seed_categories()
        seed_transactions()
        seed_investments()
        
        # Display summary
        display_summary()
        
        return 0
        
    except Exception as e:
        print(f"❌ Seeding failed: {str(e)}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
