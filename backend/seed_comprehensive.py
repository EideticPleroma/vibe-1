#!/usr/bin/env python3
"""
Comprehensive Database Seeding Script for Personal Finance App
Merges functionality from seed_data.py and seed_budgeting_data.py
Creates a realistic financial profile with categories, transactions, investments, income records, and alerts
"""

import sys
import os
from datetime import datetime, date, timedelta
from random import uniform, choice, randint, random
import json

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from models import (
    db, Category, Transaction, Investment, Income, Alert, NotificationPreference,
    get_total_income, get_total_expenses, get_net_income, BudgetMethodology, BudgetGoal
)
from app import create_app


def clear_existing_data():
    """Clear all existing data from the database"""
    print("🧹 Clearing existing data...")
    
    # Delete in order of dependencies
    db.session.query(Alert).delete()
    db.session.query(NotificationPreference).delete()
    db.session.query(Transaction).delete()
    db.session.query(Income).delete()
    db.session.query(Investment).delete()
    db.session.query(BudgetMethodology).delete()
    db.session.query(Category).delete()
    
    db.session.commit()
    print("✅ Existing data cleared")


# Merge categories from both scripts, remove duplicates
def seed_categories():
    """Create comprehensive set of categories with budgeting features"""
    print("📂 Creating comprehensive categories...")

    categories_data = [
        # Income categories from seed_comprehensive.py
        {'name': 'Salary', 'type': 'income', 'color': '#10B981'},
        {'name': 'Freelance', 'type': 'income', 'color': '#3B82F6'},
        {'name': 'Investment Returns', 'type': 'income', 'color': '#22C55E'},
        {'name': 'Side Business', 'type': 'income', 'color': '#06B6D4'},

        # Expense categories combining both scripts
        # Critical
        {'name': 'Rent/Mortgage', 'type': 'expense', 'color': '#EF4444', 'budget_limit': 1800.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'critical'},
        {'name': 'Utilities', 'type': 'expense', 'color': '#F97316', 'budget_limit': 250.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'critical'},
        {'name': 'Insurance', 'type': 'expense', 'color': '#DC2626', 'budget_limit': 180.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'critical'},

        # Essential
        {'name': 'Groceries', 'type': 'expense', 'color': '#059669', 'budget_limit': 600.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'essential'},
        {'name': 'Transportation', 'type': 'expense', 'color': '#0891B2', 'budget_limit': 320.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'essential'},
        {'name': 'Healthcare', 'type': 'expense', 'color': '#7C3AED', 'budget_limit': 150.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'essential'},
        {'name': 'Phone & Internet', 'type': 'expense', 'color': '#2563EB', 'budget_limit': 120.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'essential'},

        # Important
        {'name': 'Dining Out', 'type': 'expense', 'color': '#F59E0B', 'budget_limit': 300.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'important'},
        {'name': 'Shopping', 'type': 'expense', 'color': '#EC4899', 'budget_limit': 250.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'important'},
        {'name': 'Gym & Fitness', 'type': 'expense', 'color': '#8B5CF6', 'budget_limit': 80.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'important'},
        {'name': 'Personal Care', 'type': 'expense', 'color': '#F472B6', 'budget_limit': 100.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'important'},
        {'name': 'Education', 'type': 'expense', 'color': '#84CC16', 'budget_limit': 250.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'important'},

        # Discretionary
        {'name': 'Entertainment', 'type': 'expense', 'color': '#06B6D4', 'budget_limit': 200.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'discretionary'},
        {'name': 'Subscriptions', 'type': 'expense', 'color': '#84CC16', 'budget_limit': 85.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'discretionary'},
        {'name': 'Travel', 'type': 'expense', 'color': '#F97316', 'budget_limit': 400.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'discretionary'},
        {'name': 'Gifts & Donations', 'type': 'expense', 'color': '#EF4444', 'budget_limit': 150.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'discretionary'},
        {'name': 'Hobbies', 'type': 'expense', 'color': '#8B5CF6', 'budget_limit': 120.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'discretionary'},
        {'name': 'Miscellaneous', 'type': 'expense', 'color': '#6B7280', 'budget_limit': 100.0, 'budget_period': 'monthly', 'budget_type': 'fixed', 'budget_priority': 'discretionary'},
    ]

    categories = []
    for cat_data in categories_data:
        category = Category(**cat_data)
        categories.append(category)
        db.session.add(category)
    
    db.session.commit()
    print(f"✅ Created {len(categories)} categories")
    return categories


def seed_methodologies():
    """Create sample budget methodologies"""
    print("📊 Creating budget methodologies...")
    
    methodologies_data = [
        {
            'name': 'Zero-Based Budgeting',
            'description': 'Assign every dollar a job',
            'methodology_type': 'zero_based',
            'is_active': True,
            'is_default': True,
            'configuration': {}  # No specific config needed
        },
        {
            'name': '50/30/20 Rule',
            'description': '50% needs, 30% wants, 20% savings',
            'methodology_type': 'percentage_based',
            'is_active': False,
            'is_default': False,
            'configuration': {
                'needs_percentage': 50,
                'wants_percentage': 30,
                'savings_percentage': 20
            }
        },
        {
            'name': 'Envelope System',
            'description': 'Allocate cash to envelopes for each category',
            'methodology_type': 'envelope',
            'is_active': False,
            'is_default': False,
            'configuration': {
                'allow_envelope_transfer': True,
                'rollover_unused': True,
                'max_transfer_percentage': 10
            }
        }
    ]
    
    methodologies = []
    for meth_data in methodologies_data:
        methodology = BudgetMethodology(**meth_data)
        methodology.set_configuration(meth_data['configuration'])
        methodologies.append(methodology)
        db.session.add(methodology)
    
    db.session.commit()
    print(f"✅ Created {len(methodologies)} budget methodologies")
    return methodologies


def seed_goals(categories):
    """Create sample budget goals and link to categories"""
    print("🎯 Creating budget goals...")
    
    # Sample goals data
    goals_data = [
        {
            'name': 'Emergency Fund',
            'description': 'Build 6 months of expenses',
            'target_amount': 15000.0,
            'deadline': date.today() + timedelta(days=365),
            'category_names': ['Savings', 'Investment Returns']  # Link to these categories
        },
        {
            'name': 'Vacation Savings',
            'description': 'Save for family vacation',
            'target_amount': 5000.0,
            'deadline': date.today() + timedelta(days=180),
            'category_names': ['Side Business', 'Freelance']
        },
        {
            'name': 'New Car Down Payment',
            'description': 'Save for car purchase',
            'target_amount': 10000.0,
            'deadline': date.today() + timedelta(days=270),
            'category_names': ['Salary']
        }
    ]
    
    goals = []
    for goal_data in goals_data:
        goal = BudgetGoal(
            name=goal_data['name'],
            description=goal_data['description'],
            target_amount=goal_data['target_amount'],
            deadline=goal_data['deadline']
        )
        
        # Link categories
        for cat_name in goal_data['category_names']:
            category = next((c for c in categories if c.name == cat_name), None)
            if category:
                goal.categories.append(category)
        
        goals.append(goal)
        db.session.add(goal)
    
    db.session.commit()
    print(f"✅ Created {len(goals)} budget goals")
    return goals


def seed_income_records(categories):
    """Create income records for income tracking"""
    print("💰 Creating income records...")
    
    income_categories = [c for c in categories if c.type == 'income']
    salary_category = next((c for c in income_categories if c.name == 'Salary'), None)
    freelance_category = next((c for c in income_categories if c.name == 'Freelance'), None)
    
    income_records = []
    base_date = date.today() - timedelta(days=180)  # 6 months of data
    
    # Monthly salary records
    current_date = base_date
    while current_date <= date.today():
        if salary_category:
            # Bi-weekly salary (twice per month)
            for week in [1, 3]:  # 1st and 3rd week of month
                salary_date = current_date.replace(day=min(week * 7, 28))
                if salary_date <= date.today():
                    income = Income(
                        amount=1750.0,  # $3500/month split into bi-weekly
                        source_name='Primary Employment',
                        income_type='salary',
                        frequency='bi-weekly',
                        is_bonus=False
                    )
                    income_records.append(income)
                    db.session.add(income)
        
        # Monthly freelance income (not every month)
        if freelance_category and random() > 0.4:  # 60% chance each month
            freelance_date = current_date + timedelta(days=randint(5, 25))
            if freelance_date <= date.today():
                income = Income(
                    amount=round(uniform(200, 800), 2),
                    source_name='Freelance Client',
                    income_type='freelance',
                    frequency='irregular',
                    is_bonus=False
                )
                income_records.append(income)
                db.session.add(income)
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Add some investment returns
    investment_category = next((c for c in income_categories if c.name == 'Investment Returns'), None)
    if investment_category:
        for i in range(6):  # Monthly investment returns
            return_date = base_date + timedelta(days=30*i + randint(10, 25))
            if return_date <= date.today():
                income = Income(
                    amount=round(uniform(50, 300), 2),
                    source_name='Investment Portfolio',
                    income_type='investments',
                    frequency='monthly',
                    is_bonus=False
                )
                income_records.append(income)
                db.session.add(income)
    
    db.session.commit()
    print(f"✅ Created {len(income_records)} income records")
    return income_records


# Use the transaction seeding from seed_comprehensive.py as it's more detailed
def seed_transactions(categories):
    """Create comprehensive transaction history"""
    print("💳 Creating comprehensive transactions...")
    
    expense_categories = [c for c in categories if c.type == 'expense']
    income_categories = [c for c in categories if c.type == 'income']
    
    # Transaction templates with realistic patterns
    transaction_templates = {
        # Fixed monthly expenses
        'Rent/Mortgage': {'amount': -1800, 'frequency': 30, 'variation': 0.0, 'descriptions': ['Monthly rent payment', 'Mortgage payment']},
        'Insurance': {'amount': -350, 'frequency': 30, 'variation': 0.05, 'descriptions': ['Auto insurance', 'Health insurance', 'Life insurance']},
        
        # Regular but variable expenses
        'Groceries': {'amount': -85, 'frequency': 4, 'variation': 0.3, 'descriptions': ['Grocery shopping', 'Supermarket', 'Whole Foods', 'Trader Joes']},
        'Utilities': {'amount': -75, 'frequency': 8, 'variation': 0.4, 'descriptions': ['Electric bill', 'Gas bill', 'Internet bill', 'Water bill']},
        'Transportation': {'amount': -45, 'frequency': 5, 'variation': 0.5, 'descriptions': ['Gas fill-up', 'Public transport', 'Uber ride', 'Car maintenance']},
        'Healthcare': {'amount': -80, 'frequency': 20, 'variation': 1.0, 'descriptions': ['Doctor visit', 'Pharmacy', 'Dental checkup', 'Physical therapy']},
        
        # Lifestyle expenses
        'Dining Out': {'amount': -35, 'frequency': 3, 'variation': 0.8, 'descriptions': ['Restaurant dinner', 'Coffee shop', 'Lunch out', 'Fast food']},
        'Entertainment': {'amount': -45, 'frequency': 7, 'variation': 1.2, 'descriptions': ['Movie night', 'Concert', 'Theater', 'Sports event']},
        'Personal Care': {'amount': -40, 'frequency': 10, 'variation': 0.6, 'descriptions': ['Haircut', 'Gym membership', 'Spa', 'Skincare']},
        'Shopping': {'amount': -120, 'frequency': 12, 'variation': 1.5, 'descriptions': ['Online shopping', 'Clothing store', 'Electronics', 'Home goods']},
        'Subscriptions': {'amount': -25, 'frequency': 30, 'variation': 0.2, 'descriptions': ['Netflix', 'Spotify', 'Software subscription', 'Magazine']},
        
        # Occasional expenses
        'Education': {'amount': -180, 'frequency': 45, 'variation': 0.7, 'descriptions': ['Online course', 'Book purchase', 'Workshop', 'Certification']},
        'Travel': {'amount': -300, 'frequency': 60, 'variation': 2.0, 'descriptions': ['Flight booking', 'Hotel stay', 'Road trip', 'Weekend getaway']},
        'Gifts & Donations': {'amount': -75, 'frequency': 25, 'variation': 1.0, 'descriptions': ['Birthday gift', 'Charity donation', 'Wedding gift', 'Holiday gift']},
        
        # Income
        'Salary': {'amount': 1750, 'frequency': 14, 'variation': 0.0, 'descriptions': ['Salary deposit', 'Payroll direct deposit']},
        'Freelance': {'amount': 400, 'frequency': 35, 'variation': 0.8, 'descriptions': ['Freelance payment', 'Contract work', 'Consulting fee']},
        'Investment Returns': {'amount': 120, 'frequency': 30, 'variation': 1.5, 'descriptions': ['Dividend payment', 'Interest income', 'Capital gains']},
        'Side Business': {'amount': 200, 'frequency': 20, 'variation': 1.2, 'descriptions': ['Side business income', 'Etsy sales', 'Tutoring payment']}
    }
    
    transactions = []
    base_date = date.today() - timedelta(days=180)  # 6 months of data
    
    # Create transactions based on templates
    for category in categories:
        if category.name in transaction_templates:
            template = transaction_templates[category.name]
            current_date = base_date
            
            while current_date <= date.today():
                # Calculate amount with variation
                base_amount = template['amount']
                variation = template['variation']
                amount_multiplier = uniform(1 - variation, 1 + variation)
                amount = round(base_amount * amount_multiplier, 2)
                
                # Add date variation (±3 days)
                date_variation = randint(-3, 3)
                transaction_date = current_date + timedelta(days=date_variation)
                
                if transaction_date <= date.today():
                    description = choice(template['descriptions'])
                    
                    transaction = Transaction(
                        amount=amount,
                        category_id=category.id,
                        type=category.type,
                        date=transaction_date,
                        description=f"{description} - {transaction_date.strftime('%m/%d')}"
                    )
                    transactions.append(transaction)
                    db.session.add(transaction)
                
                # Move to next occurrence
                current_date += timedelta(days=template['frequency'])
    
    # Add some completely random transactions for realism
    print("   Adding random transactions for variety...")
    for i in range(100):
        random_category = choice(expense_categories)
        random_date = base_date + timedelta(days=randint(0, 180))
        random_amount = round(uniform(5, 150), 2)
        
        transaction = Transaction(
            amount=-random_amount,
            category_id=random_category.id,
            type='expense',
            date=random_date,
            description=f"Misc {random_category.name.lower()}"
        )
        transactions.append(transaction)
        db.session.add(transaction)
    
    db.session.commit()
    print(f"✅ Created {len(transactions)} transactions")
    return transactions


# Use investment seeding from seed_comprehensive.py as it's more comprehensive
def seed_investments():
    """Create diverse investment portfolio"""
    print("📈 Creating investment portfolio...")
    
    investments_data = [
        # Blue chip stocks
        {
            'asset_name': 'AAPL',
            'asset_type': 'stock',
            'quantity': 25.0,
            'purchase_price': 145.0,
            'current_price': 175.0,
            'purchase_date': date.today() - timedelta(days=120)
        },
        {
            'asset_name': 'MSFT',
            'asset_type': 'stock',
            'quantity': 15.0,
            'purchase_price': 280.0,
            'current_price': 320.0,
            'purchase_date': date.today() - timedelta(days=150)
        },
        {
            'asset_name': 'GOOGL',
            'asset_type': 'stock',
            'quantity': 8.0,
            'purchase_price': 2100.0,
            'current_price': 2350.0,
            'purchase_date': date.today() - timedelta(days=90)
        },
        
        # Growth stocks
        {
            'asset_name': 'TSLA',
            'asset_type': 'stock',
            'quantity': 12.0,
            'purchase_price': 220.0,
            'current_price': 185.0,  # Some losses for realism
            'purchase_date': date.today() - timedelta(days=75)
        },
        {
            'asset_name': 'NVDA',
            'asset_type': 'stock',
            'quantity': 5.0,
            'purchase_price': 400.0,
            'current_price': 485.0,
            'purchase_date': date.today() - timedelta(days=60)
        },
        
        # ETFs
        {
            'asset_name': 'VTI',
            'asset_type': 'etf',
            'quantity': 50.0,
            'purchase_price': 200.0,
            'current_price': 215.0,
            'purchase_date': date.today() - timedelta(days=200)
        },
        {
            'asset_name': 'VOO',
            'asset_type': 'etf',
            'quantity': 25.0,
            'purchase_price': 380.0,
            'current_price': 395.0,
            'purchase_date': date.today() - timedelta(days=180)
        },
        {
            'asset_name': 'QQQ',
            'asset_type': 'etf',
            'quantity': 15.0,
            'purchase_price': 330.0,
            'current_price': 350.0,
            'purchase_date': date.today() - timedelta(days=100)
        },
        
        # Cryptocurrency
        {
            'asset_name': 'BTC',
            'asset_type': 'crypto',
            'quantity': 0.5,
            'purchase_price': 45000.0,
            'current_price': 42000.0,
            'purchase_date': date.today() - timedelta(days=45)
        },
        {
            'asset_name': 'ETH',
            'asset_type': 'crypto',
            'quantity': 3.0,
            'purchase_price': 2800.0,
            'current_price': 3100.0,
            'purchase_date': date.today() - timedelta(days=30)
        },
        
        # Bonds
        {
            'asset_name': 'TLT',
            'asset_type': 'bond',
            'quantity': 20.0,
            'purchase_price': 110.0,
            'current_price': 108.0,
            'purchase_date': date.today() - timedelta(days=160)
        },
        {
            'asset_name': 'TIPS',
            'asset_type': 'bond',
            'quantity': 30.0,
            'purchase_price': 95.0,
            'current_price': 97.0,
            'purchase_date': date.today() - timedelta(days=140)
        }
    ]
    
    investments = []
    for inv_data in investments_data:
        investment = Investment(**inv_data)
        investments.append(investment)
        db.session.add(investment)
    
    db.session.commit()
    print(f"✅ Created {len(investments)} investments")
    return investments


def seed_notifications_and_alerts():
    """Create notification preferences and sample alerts"""
    print("🔔 Creating notification preferences and alerts...")
    
    # Create default notification preferences
    notification_prefs = [
        NotificationPreference(
            in_app_enabled=True,
            email_enabled=True,
            sms_enabled=False,
            push_enabled=True,
            quiet_hours_start='22:00',
            quiet_hours_end='07:00'
        )
    ]
    
    for pref in notification_prefs:
        db.session.add(pref)
    
    # Create sample alerts - need to get category IDs first
    from models import Category
    dining_category = Category.query.filter_by(name='Dining Out').first()
    shopping_category = Category.query.filter_by(name='Shopping').first()
    entertainment_category = Category.query.filter_by(name='Entertainment').first()
    
    alerts = [
        Alert(
            type='budget_threshold',
            category_id=dining_category.id if dining_category else None,
            message='You have exceeded your dining out budget by $45 this month',
            severity='high',
            channels='in_app,email',
            status='active',
            created_at=datetime.now() - timedelta(days=2)
        ),
        Alert(
            type='anomaly',
            category_id=None,  # Investment alert without category
            message='AAPL has gained 15% since your purchase. Consider reviewing your position.',
            severity='medium',
            channels='in_app',
            status='active',
            created_at=datetime.now() - timedelta(days=1)
        ),
        Alert(
            type='pace',
            category_id=shopping_category.id if shopping_category else None,
            message='You are 80% through your shopping budget with 10 days left in the month',
            severity='medium',
            channels='in_app',
            status='dismissed',
            created_at=datetime.now() - timedelta(days=5)
        ),
        Alert(
            type='variance',
            category_id=None,  # Income alert
            message='Your freelance income this month is 40% below your 3-month average',
            severity='low',
            channels='in_app',
            status='active',
            created_at=datetime.now() - timedelta(hours=8)
        ),
        Alert(
            type='budget_threshold',
            category_id=entertainment_category.id if entertainment_category else None,
            message='Entertainment spending has exceeded budget by $25',
            severity='medium',
            channels='in_app',
            status='dismissed',
            created_at=datetime.now() - timedelta(days=7)
        )
    ]
    
    for alert in alerts:
        db.session.add(alert)
    
    db.session.commit()
    print(f"✅ Created {len(notification_prefs)} notification preferences and {len(alerts)} alerts")
    return notification_prefs, alerts


def print_summary(categories, income_records, transactions, investments, notification_prefs, alerts, methodologies, goals):
    """Print comprehensive summary of seeded data"""
    print("\n" + "="*60)
    print("🎉 COMPREHENSIVE DATABASE SEEDING COMPLETED!")
    print("="*60)
    
    # Basic counts
    print(f"\n📊 Data Summary:")
    print(f"   Categories: {len(categories)}")
    print(f"   - Income categories: {len([c for c in categories if c.type == 'income'])}")
    print(f"   - Expense categories: {len([c for c in categories if c.type == 'expense'])}")
    print(f"   Income Records: {len(income_records)}")
    print(f"   Transactions: {len(transactions)}")
    print(f"   Investments: {len(investments)}")
    print(f"   Notification Preferences: {len(notification_prefs)}")
    print(f"   Alerts: {len(alerts)}")
    print(f"   Methodologies: {len(methodologies)}")
    print(f"   Goals: {len(goals)}")
    
    # Financial summary
    current_month_start = date.today().replace(day=1)
    total_income = get_total_income(current_month_start, date.today())
    total_expenses = get_total_expenses(current_month_start, date.today())
    net_income = get_net_income(current_month_start, date.today())
    
    print(f"\n💰 Current Month Financial Summary:")
    print(f"   Total Income: ${total_income:,.2f}")
    print(f"   Total Expenses: ${abs(total_expenses):,.2f}")
    print(f"   Net Income: ${net_income:,.2f}")
    print(f"   Savings Rate: {(net_income/total_income*100) if total_income > 0 else 0:.1f}%")
    
    # Investment summary
    total_investment_value = sum(inv.current_value for inv in investments)
    total_investment_cost = sum(inv.total_invested for inv in investments)
    total_gain_loss = total_investment_value - total_investment_cost
    
    print(f"\n📈 Investment Portfolio Summary:")
    print(f"   Total Portfolio Value: ${total_investment_value:,.2f}")
    print(f"   Total Cost Basis: ${total_investment_cost:,.2f}")
    print(f"   Total Gain/Loss: ${total_gain_loss:,.2f} ({(total_gain_loss/total_investment_cost*100) if total_investment_cost > 0 else 0:.1f}%)")
    
    # Budget analysis
    expense_categories = [c for c in categories if c.type == 'expense' and c.budget_limit]
    total_budget = sum(float(c.budget_limit) for c in expense_categories)
    
    print(f"\n💳 Budget Summary:")
    print(f"   Total Monthly Budget: ${total_budget:,.2f}")
    print(f"   Budget Utilization: {(abs(total_expenses)/total_budget*100) if total_budget > 0 else 0:.1f}%")
    
    # Sample data previews
    print(f"\n🔍 Sample Data Preview:")
    print(f"\nTop 5 Expense Categories:")
    for cat in sorted([c for c in categories if c.type == 'expense' and c.budget_limit], 
                     key=lambda x: float(x.budget_limit), reverse=True)[:5]:
        print(f"   - {cat.name}: ${float(cat.budget_limit):,.2f}/month ({cat.budget_priority})")
    
    print(f"\nRecent Transactions:")
    recent_txs = sorted(transactions, key=lambda x: x.date, reverse=True)[:5]
    for tx in recent_txs:
        category_name = next((c.name for c in categories if c.id == tx.category_id), 'Unknown')
        print(f"   - {tx.date}: {tx.description} - ${tx.amount} ({category_name})")
    
    print(f"\nTop Performing Investments:")
    sorted_investments = sorted(investments, key=lambda x: x.gain_loss_percentage, reverse=True)[:3]
    for inv in sorted_investments:
        print(f"   - {inv.asset_name}: {inv.gain_loss_percentage:.1f}% (${inv.total_gain_loss:,.2f})")
    
    print(f"\n🔔 Active Alerts:")
    active_alerts = [a for a in alerts if a.status == 'active']
    for alert in active_alerts[:3]:
        print(f"   - {alert.type}: {alert.message}")
    
    print(f"\n🚀 Ready for Testing:")
    print(f"   - Financial dashboard with real data")
    print(f"   - Budget tracking and alerts")
    print(f"   - Investment portfolio analysis")
    print(f"   - Income vs expense reporting")
    print(f"   - Notification system testing")
    print(f"   - 6 months of historical data available")
    
    print("\n" + "="*60)


def seed_comprehensive_database():
    """Main function to seed the entire database with comprehensive data"""
    print("🌱 Starting comprehensive database seeding...")
    
    # Create Flask app context
    app = create_app()
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        
        # Clear existing data
        clear_existing_data()
        
        # Seed data in order of dependencies
        categories = seed_categories()
        methodologies = seed_methodologies()
        goals = seed_goals(categories)
        income_records = seed_income_records(categories)
        transactions = seed_transactions(categories)
        investments = seed_investments()
        notification_prefs, alerts = seed_notifications_and_alerts()
        
        # Print comprehensive summary
        print_summary(categories, income_records, transactions, investments, notification_prefs, alerts, methodologies, goals)


if __name__ == "__main__":
    try:
        seed_comprehensive_database()
    except Exception as e:
        print(f"❌ Seeding failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
