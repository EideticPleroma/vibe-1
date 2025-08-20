#!/usr/bin/env python3
"""
Seed script for Budgeting Features Testing
Creates sample categories, transactions, and budget configurations for testing the enhanced budgeting system.
"""

import sys
import os
from datetime import datetime, date, timedelta
from random import uniform, choice, randint

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from models import db, Category, Transaction, Investment
from app import create_app


def seed_budgeting_data():
    """Seed the database with sample budgeting data"""
    print("🌱 Starting database seeding for budgeting features...")

    # Create Flask app context
    app = create_app()
    with app.app_context():

        # Clear existing data
        print("🧹 Clearing existing data...")
        db.session.query(Transaction).delete()
        db.session.query(Category).delete()
        db.session.query(Investment).delete()
        db.session.commit()

        # Create sample categories with enhanced budgeting features
        print("📂 Creating sample categories with budgeting...")

        categories_data = [
            # Essential expenses
            {
                'name': 'Rent/Mortgage',
                'type': 'expense',
                'color': '#FF6B6B',
                'budget_limit': 1800.0,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'critical'
            },
            {
                'name': 'Groceries',
                'type': 'expense',
                'color': '#4ECDC4',
                'budget_limit': 600.0,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'essential'
            },
            {
                'name': 'Utilities',
                'type': 'expense',
                'color': '#45B7D1',
                'budget_limit': 300.0,
                'budget_period': 'monthly',
                'budget_type': 'percentage',
                'budget_percentage': 8.0,  # 8% of income
                'budget_priority': 'essential'
            },
            {
                'name': 'Transportation',
                'type': 'expense',
                'color': '#96CEB4',
                'budget_limit': 400.0,
                'budget_period': 'monthly',
                'budget_type': 'rolling_average',
                'budget_rolling_months': 3,
                'budget_priority': 'essential'
            },

            # Important expenses
            {
                'name': 'Dining Out',
                'type': 'expense',
                'color': '#FFEAA7',
                'budget_limit': 300.0,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'important'
            },
            {
                'name': 'Entertainment',
                'type': 'expense',
                'color': '#DDA0DD',
                'budget_limit': 150.0,
                'budget_period': 'weekly',
                'budget_type': 'fixed',
                'budget_priority': 'important'
            },

            # Discretionary expenses
            {
                'name': 'Shopping',
                'type': 'expense',
                'color': '#98D8C8',
                'budget_limit': 200.0,
                'budget_period': 'monthly',
                'budget_type': 'fixed',
                'budget_priority': 'discretionary'
            },

            # Income categories
            {
                'name': 'Salary',
                'type': 'income',
                'color': '#00FF00'
            },
            {
                'name': 'Freelance',
                'type': 'income',
                'color': '#32CD32'
            }
        ]

        categories = []
        for cat_data in categories_data:
            category = Category(**cat_data)
            categories.append(category)
            db.session.add(category)

        db.session.commit()
        print(f"✅ Created {len(categories)} categories")

        # Create sample transactions for the past 90 days
        print("💳 Creating sample transactions...")

        expense_categories = [c for c in categories if c.type == 'expense']
        income_categories = [c for c in categories if c.type == 'income']

        # Transaction templates with realistic amounts
        transaction_templates = {
            'Rent/Mortgage': {'amount': -1800, 'frequency': 30, 'description': 'Monthly rent payment'},
            'Groceries': {'amount': -85, 'frequency': 4, 'description': 'Grocery shopping'},
            'Utilities': {'amount': -150, 'frequency': 25, 'description': 'Electric bill'},
            'Transportation': {'amount': -60, 'frequency': 3, 'description': 'Gas fill-up'},
            'Dining Out': {'amount': -45, 'frequency': 7, 'description': 'Restaurant dinner'},
            'Entertainment': {'amount': -25, 'frequency': 5, 'description': 'Movie night'},
            'Shopping': {'amount': -75, 'frequency': 10, 'description': 'Online shopping'},
            'Salary': {'amount': 3500, 'frequency': 14, 'description': 'Salary deposit'},
            'Freelance': {'amount': 500, 'frequency': 20, 'description': 'Freelance payment'}
        }

        transactions_created = 0
        base_date = date.today() - timedelta(days=90)

        for category in categories:
            if category.name in transaction_templates:
                template = transaction_templates[category.name]
                current_date = base_date

                while current_date <= date.today():
                    # Add some randomness to amounts and dates
                    amount_variation = uniform(0.8, 1.2)  # ±20% variation
                    amount = template['amount'] * amount_variation

                    # Add some random date variation (±2 days)
                    date_variation = randint(-2, 2)
                    transaction_date = current_date + timedelta(days=date_variation)

                    if transaction_date <= date.today():
                        transaction = Transaction(
                            amount=round(amount, 2),
                            category_id=category.id,
                            type=category.type,
                            date=transaction_date,
                            description=f"{template['description']} - {transaction_date.strftime('%m/%d')}"
                        )
                        db.session.add(transaction)
                        transactions_created += 1

                    current_date += timedelta(days=template['frequency'])

        # Add some random transactions for variety
        for i in range(50):
            random_category = choice(expense_categories)
            random_date = base_date + timedelta(days=randint(0, 90))
            random_amount = round(uniform(10, 200), 2)

            transaction = Transaction(
                amount=-random_amount,
                category_id=random_category.id,
                type='expense',
                date=random_date,
                description=f"Random {random_category.name.lower()} expense"
            )
            db.session.add(transaction)
            transactions_created += 1

        db.session.commit()
        print(f"✅ Created {transactions_created} transactions")

        # Create sample investments
        print("📈 Creating sample investments...")

        investments_data = [
            {
                'asset_name': 'AAPL',
                'asset_type': 'stock',
                'quantity': 50.0,
                'purchase_price': 150.0,
                'current_price': 175.0,
                'purchase_date': date.today() - timedelta(days=180)
            },
            {
                'asset_name': 'GOOGL',
                'asset_type': 'stock',
                'quantity': 25.0,
                'purchase_price': 120.0,
                'current_price': 140.0,
                'purchase_date': date.today() - timedelta(days=120)
            },
            {
                'asset_name': 'BTC',
                'asset_type': 'crypto',
                'quantity': 2.5,
                'purchase_price': 35000.0,
                'current_price': 42000.0,
                'purchase_date': date.today() - timedelta(days=60)
            }
        ]

        for inv_data in investments_data:
            investment = Investment(**inv_data)
            db.session.add(investment)

        db.session.commit()
        print(f"✅ Created {len(investments_data)} investments")

        # Print summary
        print("\n" + "="*50)
        print("🎉 DATABASE SEEDED SUCCESSFULLY!")
        print("="*50)

        print("\n📊 Summary:")
        print(f"   Categories: {len(categories)}")
        print(f"   - Expense categories: {len(expense_categories)}")
        print(f"   - Income categories: {len(income_categories)}")
        print(f"   Transactions: {transactions_created}")
        print(f"   Investments: {len(investments_data)}")

        print("\n💡 Budgeting Features Demonstrated:")
        print("   ✅ Fixed budget amounts (Rent, Groceries)")
        print("   ✅ Percentage-based budgets (Utilities - 8% of income)")
        print("   ✅ Rolling average budgets (Transportation - 3 months)")
        print("   ✅ Different time periods (weekly entertainment budget)")
        print("   ✅ Priority levels (critical, essential, important, discretionary)")

        print("\n🚀 Ready for Testing:")
        print("   - Test budget calculations with GET /api/budget/calculate-effective")
        print("   - Test budget suggestions with GET /api/budget/suggestions")
        print("   - Test dashboard with budget progress tracking")
        print("   - Test budget alerts and notifications")

        print("\n" + "="*50)


if __name__ == "__main__":
    try:
        seed_budgeting_data()
    except Exception as e:
        print(f"❌ Seeding failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
