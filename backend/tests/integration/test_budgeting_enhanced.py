#!/usr/bin/env python3
"""
Unit tests for Enhanced Budgeting Features (Feature 1001)
Tests the enhanced budget planning functionality including:
- Flexible budget periods
- Multiple budget types
- Priority-based budgeting
- Automated suggestions
- Template copying
"""

import unittest
import json
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from models import db, Category, Transaction
from app import create_app
try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    # Fallback if dateutil is not installed
    def relativedelta(months):
        class MockRelativedelta:
            def __init__(self, months):
                self.months = months
        return MockRelativedelta(months)


class TestEnhancedBudgeting(unittest.TestCase):
    """Test cases for enhanced budgeting features"""

    def setUp(self):
        """Set up test environment"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create tables
        db.create_all()

        # Create test data
        self.test_category = Category(
            name='Test Expenses',
            type='expense',
            color='#FF5733',
            budget_limit=500.0,
            budget_period='monthly',
            budget_type='fixed',
            budget_priority='essential',
            budget_percentage=None,
            budget_rolling_months=3
        )
        db.session.add(self.test_category)
        db.session.commit()

    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_category_model_enhanced_fields(self):
        """Test that Category model has all enhanced budget fields"""
        category = Category.query.first()
        self.assertIsNotNone(category)
        self.assertEqual(category.budget_period, 'monthly')
        self.assertEqual(category.budget_type, 'fixed')
        self.assertEqual(category.budget_priority, 'essential')
        self.assertEqual(category.budget_rolling_months, 3)

    def test_calculate_effective_budget_fixed(self):
        """Test effective budget calculation for fixed type"""
        category = Category.query.first()
        effective = category.calculate_effective_budget()
        self.assertEqual(effective, 500.0)

    def test_calculate_effective_budget_percentage(self):
        """Test effective budget calculation for percentage type"""
        category = Category.query.first()
        category.budget_type = 'percentage'
        category.budget_percentage = 15.0
        effective = category.calculate_effective_budget(total_income=3000.0)
        self.assertEqual(effective, 450.0)  # 15% of 3000

    def test_calculate_effective_budget_rolling_average(self):
        """Test effective budget calculation for rolling average type"""
        category = Category.query.first()
        category.budget_type = 'rolling_average'
        effective = category.calculate_effective_budget()
        self.assertEqual(effective, 500.0)  # Placeholder implementation

    def test_get_budget_period_days(self):
        """Test budget period days calculation"""
        category = Category.query.first()

        # Test different periods
        category.budget_period = 'daily'
        self.assertEqual(category.get_budget_period_days(), 1)

        category.budget_period = 'weekly'
        self.assertEqual(category.get_budget_period_days(), 7)

        category.budget_period = 'monthly'
        self.assertEqual(category.get_budget_period_days(), 30)

        category.budget_period = 'yearly'
        self.assertEqual(category.get_budget_period_days(), 365)

    def test_category_to_dict_includes_enhanced_fields(self):
        """Test that to_dict includes all enhanced budget fields"""
        category = Category.query.first()
        data = category.to_dict()

        self.assertIn('budget_period', data)
        self.assertIn('budget_type', data)
        self.assertIn('budget_priority', data)
        self.assertIn('budget_percentage', data)
        self.assertIn('budget_rolling_months', data)

        self.assertEqual(data['budget_period'], 'monthly')
        self.assertEqual(data['budget_type'], 'fixed')
        self.assertEqual(data['budget_priority'], 'essential')

    def test_create_category_with_enhanced_fields(self):
        """Test creating category with enhanced budget fields"""
        response = self.client.post('/api/categories', json={
            'name': 'Enhanced Test',
            'type': 'expense',
            'color': '#123456',
            'budget_limit': 750.0,
            'budget_period': 'weekly',
            'budget_type': 'percentage',
            'budget_priority': 'critical',
            'budget_percentage': 10.0,
            'budget_rolling_months': 6
        })

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['budget_period'], 'weekly')
        self.assertEqual(data['budget_type'], 'percentage')
        self.assertEqual(data['budget_priority'], 'critical')
        self.assertEqual(data['budget_percentage'], 10.0)
        self.assertEqual(data['budget_rolling_months'], 6)

    def test_create_category_validation_errors(self):
        """Test validation errors for enhanced budget fields"""
        # Test invalid budget period
        response = self.client.post('/api/categories', json={
            'name': 'Test Category',
            'type': 'expense',
            'budget_period': 'invalid'
        })
        self.assertEqual(response.status_code, 400)

        # Test invalid budget type
        response = self.client.post('/api/categories', json={
            'name': 'Test Category',
            'type': 'expense',
            'budget_type': 'invalid'
        })
        self.assertEqual(response.status_code, 400)

        # Test invalid budget priority
        response = self.client.post('/api/categories', json={
            'name': 'Test Category',
            'type': 'expense',
            'budget_priority': 'invalid'
        })
        self.assertEqual(response.status_code, 400)

        # Test percentage type without percentage value
        response = self.client.post('/api/categories', json={
            'name': 'Test Category',
            'type': 'expense',
            'budget_type': 'percentage'
        })
        self.assertEqual(response.status_code, 400)

        # Test invalid percentage range
        response = self.client.post('/api/categories', json={
            'name': 'Test Category',
            'type': 'expense',
            'budget_type': 'percentage',
            'budget_percentage': 150.0
        })
        self.assertEqual(response.status_code, 400)

    def test_update_category_enhanced_fields(self):
        """Test updating category with enhanced budget fields"""
        category = Category.query.first()

        response = self.client.put(f'/api/categories/{category.id}', json={
            'budget_period': 'yearly',
            'budget_type': 'percentage',
            'budget_percentage': 12.5,
            'budget_priority': 'important'
        })

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['budget_period'], 'yearly')
        self.assertEqual(data['budget_type'], 'percentage')
        self.assertEqual(data['budget_percentage'], 12.5)
        self.assertEqual(data['budget_priority'], 'important')

    def test_budget_suggestions_endpoint(self):
        """Test budget suggestions API endpoint"""
        # Create a category without budget
        category = Category(
            name='No Budget Category',
            type='expense',
            color='#654321'
        )
        db.session.add(category)
        db.session.commit()  # Commit to get category.id

        # Add some transaction data for the past 3 months
        base_date = date.today() - timedelta(days=90)  # Approximately 3 months
        for i in range(90):  # 90 days worth of transactions
            transaction = Transaction(
                amount=-50.0,  # $50 expense
                category_id=category.id,
                type='expense',
                date=base_date + timedelta(days=i),
                description=f'Test transaction {i}'
            )
            db.session.add(transaction)
        db.session.commit()

        response = self.client.get('/api/budget/suggestions')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('suggestions', data)
        self.assertIn('total_suggestions', data)

        # Should have suggestions for the category without budget
        self.assertGreater(len(data['suggestions']), 0)

        # Check suggestion structure
        suggestion = data['suggestions'][0]
        self.assertIn('category_id', suggestion)
        self.assertIn('category_name', suggestion)
        self.assertIn('suggested_budget', suggestion)
        self.assertIn('historical_average', suggestion)
        self.assertIn('reasoning', suggestion)

    def test_calculate_effective_budget_endpoint(self):
        """Test effective budget calculation endpoint"""
        response = self.client.post('/api/budget/calculate-effective', json={
            'total_income': 4000.0
        })

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertIn('effective_budgets', data)
        self.assertIn('total_categories', data)
        self.assertIn('total_budget', data)

        # Should have effective budget data for our test category
        self.assertGreater(len(data['effective_budgets']), 0)

        budget_data = data['effective_budgets'][0]
        self.assertIn('category_id', budget_data)
        self.assertIn('effective_amount', budget_data)
        self.assertIn('budget_type', budget_data)

    def test_copy_budget_template_endpoint(self):
        """Test budget template copying endpoint"""
        # Create a category with a budget
        category = Category(
            name='Template Test',
            type='expense',
            color='#ABCDEF',
            budget_limit=600.0,
            budget_period='monthly',
            budget_type='fixed',
            budget_priority='essential'
        )
        db.session.add(category)
        db.session.commit()

        response = self.client.post('/api/budget/copy-template', json={
            'source_period': 'last_month',
            'inflation_rate': 5.0
        })

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertIn('message', data)
        self.assertIn('updated_categories', data)
        self.assertIn('total_updated', data)

        # Check that the budget was updated with inflation
        updated_category = Category.query.filter_by(name='Template Test').first()
        expected_budget = 600.0 * 1.05  # 5% inflation
        self.assertAlmostEqual(float(updated_category.budget_limit), expected_budget, places=2)

    def test_budget_suggestions_no_data(self):
        """Test budget suggestions when no spending data exists"""
        # Create a category without budget and without transactions
        category = Category(
            name='New Category',
            type='expense',
            color='#FEDCBA'
        )
        db.session.add(category)
        db.session.commit()

        response = self.client.get('/api/budget/suggestions')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        # Should still return successfully even with no data
        self.assertIn('suggestions', data)
        self.assertEqual(len(data['suggestions']), 0)  # No suggestions without data

    def test_calculate_effective_budget_no_income(self):
        """Test effective budget calculation without income data"""
        response = self.client.post('/api/budget/calculate-effective', json={})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        # Should still work without income data (using default values)
        self.assertIn('effective_budgets', data)

        # Fixed budget should remain unchanged
        budget_data = data['effective_budgets'][0]
        self.assertEqual(budget_data['effective_amount'], 500.0)


if __name__ == '__main__':
    print("🧪 Running Enhanced Budgeting Unit Tests...")
    unittest.main(verbosity=2)
