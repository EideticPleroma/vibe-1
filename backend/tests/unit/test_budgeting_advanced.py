#!/usr/bin/env python3
"""
Test suite for Advanced Budget Tracking (Feature 1002)
Tests real-time budget monitoring, predictive analytics, and performance scoring
"""

import unittest
import json
from datetime import datetime, date, timedelta
from flask import Flask

from models import (
    db, Category, Transaction,
    get_budget_progress_advanced, get_budget_historical_trends,
    get_transaction_budget_impact, get_budget_performance_score
)
from routes import api


class TestAdvancedBudgetTracking(unittest.TestCase):
    """Test cases for advanced budget tracking functionality"""

    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.register_blueprint(api)

        db.init_app(self.app)

        with self.app.app_context():
            db.create_all()
            self._setup_test_data()

    def tearDown(self):
        """Clean up test environment"""
        with self.app.app_context():
            db.drop_all()

    def _setup_test_data(self):
        """Create test data for budget tracking"""
        # Create expense categories with budgets
        categories = [
            Category(name='Groceries', type='expense', color='#FF6B6B',
                    budget_limit=500.0, budget_period='monthly', budget_type='fixed'),
            Category(name='Entertainment', type='expense', color='#4ECDC4',
                    budget_limit=200.0, budget_period='monthly', budget_type='fixed'),
            Category(name='Transportation', type='expense', color='#45B7D1',
                    budget_limit=300.0, budget_period='monthly', budget_type='fixed'),
            Category(name='Utilities', type='expense', color='#96CEB4',
                    budget_limit=400.0, budget_period='monthly', budget_type='fixed'),
        ]

        for category in categories:
            db.session.add(category)

        # Create income category
        income_category = Category(name='Salary', type='income', color='#2ECC71')
        db.session.add(income_category)
        db.session.commit()

        # Create test transactions
        current_date = date.today()
        start_of_month = date(current_date.year, current_date.month, 1)

        # Add some transactions for current month
        transactions = [
            # Groceries - over budget
            Transaction(date=start_of_month + timedelta(days=5), amount=-150.0,
                       category_id=1, description='Weekly groceries', type='expense'),
            Transaction(date=start_of_month + timedelta(days=12), amount=-200.0,
                       category_id=1, description='More groceries', type='expense'),
            Transaction(date=start_of_month + timedelta(days=19), amount=-180.0,
                       category_id=1, description='Weekend shopping', type='expense'),

            # Entertainment - under budget
            Transaction(date=start_of_month + timedelta(days=3), amount=-50.0,
                       category_id=2, description='Movie night', type='expense'),
            Transaction(date=start_of_month + timedelta(days=15), amount=-30.0,
                       category_id=2, description='Concert tickets', type='expense'),

            # Transportation - on track
            Transaction(date=start_of_month + timedelta(days=2), amount=-80.0,
                       category_id=3, description='Gas', type='expense'),
            Transaction(date=start_of_month + timedelta(days=10), amount=-60.0,
                       category_id=3, description='Maintenance', type='expense'),

            # Utilities - warning zone
            Transaction(date=start_of_month + timedelta(days=1), amount=-120.0,
                       category_id=4, description='Electricity', type='expense'),
            Transaction(date=start_of_month + timedelta(days=8), amount=-90.0,
                       category_id=4, description='Water', type='expense'),
            Transaction(date=start_of_month + timedelta(days=16), amount=-100.0,
                       category_id=4, description='Internet', type='expense'),

            # Income
            Transaction(date=start_of_month + timedelta(days=1), amount=3000.0,
                       category_id=5, description='Monthly salary', type='income'),
        ]

        for transaction in transactions:
            db.session.add(transaction)

        db.session.commit()

    def test_budget_health_score_calculation(self):
        """Test budget health score calculation"""
        with self.app.app_context():
            # Get categories
            groceries_cat = Category.query.filter_by(name='Groceries').first()
            entertainment_cat = Category.query.filter_by(name='Entertainment').first()

            # Test health score for different scenarios
            # Groceries: spent 530 vs budget 500 (over budget, early in month)
            groceries_score = groceries_cat.get_budget_health_score(530, 10)
            self.assertLess(groceries_score, 80)  # Should be lower due to over-spending

            # Entertainment: spent 80 vs budget 200 (well under budget)
            entertainment_score = entertainment_cat.get_budget_health_score(80, 10)
            self.assertGreater(entertainment_score, 60)  # Should be reasonably high due to under-spending

            # No budget scenario
            no_budget_cat = Category.query.filter_by(name='Salary').first()
            no_budget_score = no_budget_cat.get_budget_health_score(0, 10)
            self.assertEqual(no_budget_score, 100)  # Perfect score for no budget

    def test_advanced_budget_progress(self):
        """Test advanced budget progress calculation"""
        with self.app.app_context():
            progress_data = get_budget_progress_advanced()

            # Should have 4 expense categories
            self.assertEqual(len(progress_data), 4)

            # Check structure of progress data
            for item in progress_data:
                self.assertIn('category_id', item)
                self.assertIn('category_name', item)
                self.assertIn('health_score', item)
                self.assertIn('period_info', item)
                self.assertIn('pace_analysis', item)
                self.assertIn('variance_analysis', item)

                # Validate health score range
                self.assertGreaterEqual(item['health_score'], 0)
                self.assertLessEqual(item['health_score'], 100)

                # Validate pace ratio calculation
                self.assertGreater(item['pace_analysis']['pace_ratio'], 0)

    def test_historical_trends(self):
        """Test historical budget trends"""
        with self.app.app_context():
            trends = get_budget_historical_trends(3)  # Last 3 months

            # Should have at least current month
            self.assertGreaterEqual(len(trends), 1)

            # Check structure
            for trend in trends:
                self.assertIn('period', trend)
                self.assertIn('categories', trend)
                self.assertIn('total_budgeted', trend)
                self.assertIn('total_spent', trend)
                self.assertIn('overall_progress', trend)

                # Validate totals are non-negative
                self.assertGreaterEqual(trend['total_budgeted'], 0)
                self.assertGreaterEqual(trend['total_spent'], 0)

    def test_transaction_budget_impact(self):
        """Test transaction budget impact analysis"""
        with self.app.app_context():
            # Get a transaction ID
            transaction = Transaction.query.filter_by(type='expense').first()
            self.assertIsNotNone(transaction)

            impact = get_transaction_budget_impact(transaction.id)

            # Should return impact analysis
            self.assertIsNotNone(impact)
            self.assertIn('transaction_id', impact)
            self.assertIn('category_name', impact)
            self.assertIn('severity', impact)
            self.assertIn('impact_message', impact)
            self.assertIn('recommendations', impact)

            # Validate severity levels
            valid_severities = ['low', 'warning', 'critical', 'none']
            self.assertIn(impact['severity'], valid_severities)

    def test_budget_performance_score(self):
        """Test overall budget performance scoring"""
        with self.app.app_context():
            score = get_budget_performance_score()

            # Score should be between 0 and 100
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

            # With test data, should have some meaningful score
            self.assertGreater(score, 0)

    def test_budget_progress_with_date_range(self):
        """Test budget progress with custom date range"""
        with self.app.app_context():
            current_date = date.today()
            start_of_month = date(current_date.year, current_date.month, 1)
            end_of_month = start_of_month + timedelta(days=20)

            progress_data = get_budget_progress_advanced(
                start_date=start_of_month,
                end_date=end_of_month
            )

            # Should still have 4 categories
            self.assertEqual(len(progress_data), 4)

            # Check period info reflects custom range
            for item in progress_data:
                period_info = item['period_info']
                self.assertEqual(period_info['start_date'], start_of_month.isoformat())
                self.assertEqual(period_info['end_date'], end_of_month.isoformat())
                self.assertEqual(period_info['total_days'], 20)  # 20 days range (inclusive)

    def test_predictive_overspend_calculation(self):
        """Test predictive overspend calculations"""
        with self.app.app_context():
            progress_data = get_budget_progress_advanced()

            # Find groceries category (should have overspend prediction)
            groceries_data = next(item for item in progress_data if item['category_name'] == 'Groceries')

            # Should have predicted overspend due to high spending pace
            pace_analysis = groceries_data['pace_analysis']
            self.assertGreater(pace_analysis['predicted_overspend'], 0)
            self.assertGreater(pace_analysis['pace_ratio'], 1)

    def test_variance_analysis(self):
        """Test spending variance analysis"""
        with self.app.app_context():
            progress_data = get_budget_progress_advanced()

            for item in progress_data:
                variance = item['variance_analysis']

                # Should have variance calculations
                self.assertIn('expected_spent', variance)
                self.assertIn('variance_amount', variance)
                self.assertIn('variance_percentage', variance)

                # Expected spent should be positive for budgeted categories
                if item['budget_limit'] > 0:
                    self.assertGreaterEqual(variance['expected_spent'], 0)


class TestAdvancedBudgetAPI(unittest.TestCase):
    """Test API endpoints for advanced budget tracking"""

    def setUp(self):
        """Set up test client"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.register_blueprint(api)

        db.init_app(self.app)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self._setup_test_data()

    def tearDown(self):
        """Clean up test environment"""
        with self.app.app_context():
            db.drop_all()

    def _setup_test_data(self):
        """Create test data for API tests"""
        # Create a basic expense category with budget
        category = Category(
            name='Test Category',
            type='expense',
            color='#FF6B6B',
            budget_limit=100.0,
            budget_period='monthly',
            budget_type='fixed'
        )
        db.session.add(category)
        db.session.commit()

    def test_advanced_budget_progress_endpoint(self):
        """Test advanced budget progress API endpoint"""
        with self.app.app_context():
            response = self.client.get('/api/budget/progress/advanced')
            self.assertEqual(response.status_code, 200)

            data = json.loads(response.data)
            self.assertIn('progress', data)
            self.assertIn('summary', data)
            self.assertIn('alerts', data)
            self.assertIn('generated_at', data)

    def test_historical_trends_endpoint(self):
        """Test historical trends API endpoint"""
        with self.app.app_context():
            response = self.client.get('/api/budget/trends/historical?months=3')
            self.assertEqual(response.status_code, 200)

            data = json.loads(response.data)
            self.assertIn('trends', data)
            self.assertIn('period_months', data)
            self.assertEqual(data['period_months'], 3)

    def test_performance_score_endpoint(self):
        """Test performance score API endpoint"""
        with self.app.app_context():
            response = self.client.get('/api/budget/performance-score')
            self.assertEqual(response.status_code, 200)

            data = json.loads(response.data)
            self.assertIn('performance', data)
            self.assertIn('generated_at', data)

            performance = data['performance']
            self.assertIn('overall_score', performance)
            self.assertIn('categories_tracked', performance)
            self.assertIn('score_interpretation', performance)

    def test_predictive_alerts_endpoint(self):
        """Test predictive alerts API endpoint"""
        with self.app.app_context():
            response = self.client.get('/api/budget/predictive-alerts')
            self.assertEqual(response.status_code, 200)

            data = json.loads(response.data)
            self.assertIn('alerts', data)
            self.assertIn('total_alerts', data)
            self.assertIn('high_priority', data)
            self.assertIn('medium_priority', data)

    def test_transaction_impact_endpoint(self):
        """Test transaction impact API endpoint"""
        with self.app.app_context():
            # Create a test transaction first
            category = Category.query.first()
            transaction = Transaction(
                date=date.today(),
                amount=-50.0,
                category_id=category.id,
                description='Test transaction',
                type='expense'
            )
            db.session.add(transaction)
            db.session.commit()

            response = self.client.get(f'/api/budget/transaction-impact/{transaction.id}')
            self.assertEqual(response.status_code, 200)

            data = json.loads(response.data)
            self.assertIn('impact_analysis', data)
            self.assertIn('generated_at', data)

            impact = data['impact_analysis']
            self.assertIn('transaction_id', impact)
            self.assertIn('severity', impact)
            self.assertIn('recommendations', impact)


if __name__ == '__main__':
    unittest.main()
