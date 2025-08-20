"""
Integration tests for Budget Methodology API endpoints (Feature 1005)
"""

import pytest
import json
from datetime import date

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import app
from models import db, BudgetMethodology, Category, Transaction


class TestBudgetMethodologyEndpoints:
    """Test cases for budget methodology API endpoints"""
    
    def setup_method(self):
        """Set up test environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self.create_test_data()
    
    def teardown_method(self):
        """Clean up test environment"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def create_test_data(self):
        """Create test data"""
        # Create test categories
        categories = [
            Category(name='Rent', type='expense', budget_priority='critical', budget_limit=1500.0),
            Category(name='Groceries', type='expense', budget_priority='essential', budget_limit=600.0),
            Category(name='Entertainment', type='expense', budget_priority='discretionary', budget_limit=300.0),
        ]
        
        for cat in categories:
            db.session.add(cat)
        
        # Create test transactions
        transactions = [
            Transaction(date=date.today(), amount=-1200, category_id=1, type='expense', description='Rent payment'),
            Transaction(date=date.today(), amount=-400, category_id=2, type='expense', description='Grocery shopping'),
            Transaction(date=date.today(), amount=5000, category_id=1, type='income', description='Salary'),
        ]
        
        for trans in transactions:
            db.session.add(trans)
        
        # Create test methodologies
        methodologies = [
            BudgetMethodology(
                name='Test Zero-Based',
                description='Test zero-based budgeting',
                methodology_type='zero_based',
                is_active=True,
                is_default=True
            ),
            BudgetMethodology(
                name='Test 50/30/20',
                description='Test percentage-based budgeting',
                methodology_type='percentage_based',
                is_active=False,
                is_default=False,
                configuration=json.dumps({
                    'needs_percentage': 50,
                    'wants_percentage': 30,
                    'savings_percentage': 20
                })
            ),
            BudgetMethodology(
                name='Test Envelope',
                description='Test envelope budgeting',
                methodology_type='envelope',
                is_active=False,
                is_default=False,
                configuration=json.dumps({
                    'allow_envelope_transfer': True,
                    'rollover_unused': True
                })
            )
        ]
        
        for method in methodologies:
            db.session.add(method)
        
        db.session.commit()
    
    def test_get_all_methodologies(self):
        """Test GET /api/budget/methodologies"""
        response = self.client.get('/api/budget/methodologies')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 3
        
        # Check first methodology
        methodology = data[0]
        assert 'id' in methodology
        assert 'name' in methodology
        assert 'methodology_type' in methodology
        assert 'is_active' in methodology
        assert 'configuration' in methodology
    
    def test_create_methodology(self):
        """Test POST /api/budget/methodologies"""
        new_methodology = {
            'name': 'Custom 60/20/20',
            'description': 'Custom percentage allocation',
            'methodology_type': 'percentage_based',
            'is_active': False,
            'is_default': False,
            'configuration': {
                'needs_percentage': 60,
                'wants_percentage': 20,
                'savings_percentage': 20
            }
        }
        
        response = self.client.post('/api/budget/methodologies', 
                                  json=new_methodology)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Custom 60/20/20'
        assert data['methodology_type'] == 'percentage_based'
        assert data['configuration']['needs_percentage'] == 60
    
    def test_create_methodology_validation(self):
        """Test POST /api/budget/methodologies with validation errors"""
        # Missing required fields
        response = self.client.post('/api/budget/methodologies', json={})
        assert response.status_code == 400
        
        # Invalid methodology type
        invalid_methodology = {
            'name': 'Invalid Method',
            'methodology_type': 'invalid_type'
        }
        response = self.client.post('/api/budget/methodologies', 
                                  json=invalid_methodology)
        assert response.status_code == 400
        
        # Duplicate name
        duplicate_methodology = {
            'name': 'Test Zero-Based',  # Already exists
            'methodology_type': 'zero_based'
        }
        response = self.client.post('/api/budget/methodologies', 
                                  json=duplicate_methodology)
        assert response.status_code == 400
        
        # Invalid percentage configuration
        invalid_percentage = {
            'name': 'Invalid Percentage',
            'methodology_type': 'percentage_based',
            'configuration': {
                'needs_percentage': 50,
                'wants_percentage': 30,
                'savings_percentage': 30  # Sums to 110%
            }
        }
        response = self.client.post('/api/budget/methodologies', 
                                  json=invalid_percentage)
        assert response.status_code == 400
    
    def test_update_methodology(self):
        """Test PUT /api/budget/methodologies/<id>"""
        # Get existing methodology
        response = self.client.get('/api/budget/methodologies')
        methodologies = response.get_json()
        methodology_id = methodologies[0]['id']
        
        # Update methodology
        update_data = {
            'name': 'Updated Zero-Based',
            'description': 'Updated description'
        }
        
        response = self.client.put(f'/api/budget/methodologies/{methodology_id}', 
                                 json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Zero-Based'
        assert data['description'] == 'Updated description'
    
    def test_delete_methodology(self):
        """Test DELETE /api/budget/methodologies/<id>"""
        # Create a non-active methodology to delete
        new_methodology = {
            'name': 'To Be Deleted',
            'methodology_type': 'envelope',
            'is_active': False
        }
        
        create_response = self.client.post('/api/budget/methodologies', 
                                         json=new_methodology)
        methodology_id = create_response.get_json()['id']
        
        # Delete methodology
        response = self.client.delete(f'/api/budget/methodologies/{methodology_id}')
        assert response.status_code == 200
        
        # Verify deletion by checking it's not in the list
        list_response = self.client.get('/api/budget/methodologies')
        methodologies = list_response.get_json()
        methodology_ids = [m['id'] for m in methodologies]
        assert methodology_id not in methodology_ids
    
    def test_delete_active_methodology_fails(self):
        """Test DELETE fails for active methodology"""
        # Get active methodology
        response = self.client.get('/api/budget/methodologies/active')
        active_methodology = response.get_json()
        
        # Try to delete active methodology
        response = self.client.delete(f'/api/budget/methodologies/{active_methodology["id"]}')
        assert response.status_code == 400
    
    def test_get_active_methodology(self):
        """Test GET /api/budget/methodologies/active"""
        response = self.client.get('/api/budget/methodologies/active')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_active'] is True
        assert data['name'] == 'Test Zero-Based'
    
    def test_activate_methodology(self):
        """Test POST /api/budget/methodologies/<id>/activate"""
        # Get a non-active methodology
        response = self.client.get('/api/budget/methodologies')
        methodologies = response.get_json()
        
        inactive_methodology = None
        for method in methodologies:
            if not method['is_active']:
                inactive_methodology = method
                break
        
        assert inactive_methodology is not None
        
        # Activate methodology
        response = self.client.post(f'/api/budget/methodologies/{inactive_methodology["id"]}/activate')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'activated successfully' in data['message']
        assert data['methodology']['is_active'] is True
    
    def test_calculate_methodology(self):
        """Test GET/POST /api/budget/methodologies/<id>/calculate"""
        # Get active methodology
        response = self.client.get('/api/budget/methodologies/active')
        methodology = response.get_json()
        
        # Test GET calculation (uses current income)
        response = self.client.get(f'/api/budget/methodologies/{methodology["id"]}/calculate')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'calculation_result' in data
        assert 'generated_at' in data
        
        result = data['calculation_result']
        assert 'methodology' in result
        assert 'total_income' in result
        assert 'allocations' in result or 'envelopes' in result
        
        # Test POST calculation with custom income
        calculation_request = {'total_income': 6000.0}
        response = self.client.post(f'/api/budget/methodologies/{methodology["id"]}/calculate',
                                  json=calculation_request)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['calculation_result']['total_income'] == 6000.0
    
    def test_apply_methodology(self):
        """Test POST /api/budget/methodologies/<id>/apply"""
        # Get active methodology
        response = self.client.get('/api/budget/methodologies/active')
        methodology = response.get_json()
        
        # Test apply without auto-update
        apply_request = {
            'total_income': 5000.0,
            'auto_update': False
        }
        
        response = self.client.post(f'/api/budget/methodologies/{methodology["id"]}/apply',
                                  json=apply_request)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'calculation_result' in data
        assert data['auto_updated'] is False
        
        # Test apply with auto-update
        apply_request['auto_update'] = True
        response = self.client.post(f'/api/budget/methodologies/{methodology["id"]}/apply',
                                  json=apply_request)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['auto_updated'] is True
    
    def test_validate_methodology(self):
        """Test GET /api/budget/methodologies/<id>/validate"""
        # Get percentage-based methodology
        response = self.client.get('/api/budget/methodologies')
        methodologies = response.get_json()
        
        percentage_methodology = None
        for method in methodologies:
            if method['methodology_type'] == 'percentage_based':
                percentage_methodology = method
                break
        
        assert percentage_methodology is not None
        
        # Validate methodology
        response = self.client.get(f'/api/budget/methodologies/{percentage_methodology["id"]}/validate')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'is_valid' in data
        assert 'methodology_name' in data
        assert 'configuration' in data
        assert data['is_valid'] is True
    
    def test_compare_methodologies(self):
        """Test POST /api/budget/methodologies/compare"""
        # Get all methodologies
        response = self.client.get('/api/budget/methodologies')
        methodologies = response.get_json()
        
        methodology_ids = [method['id'] for method in methodologies[:2]]
        
        compare_request = {
            'methodology_ids': methodology_ids,
            'total_income': 5000.0
        }
        
        response = self.client.post('/api/budget/methodologies/compare',
                                  json=compare_request)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'comparisons' in data
        assert 'total_income' in data
        assert len(data['comparisons']) == 2
        
        # Check comparison structure
        comparison = data['comparisons'][0]
        assert 'methodology_id' in comparison
        assert 'methodology_name' in comparison
        assert 'calculation_result' in comparison
    
    def test_get_methodology_recommendations(self):
        """Test GET /api/budget/methodologies/recommendations"""
        response = self.client.get('/api/budget/methodologies/recommendations')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'recommendations' in data
        assert 'user_profile' in data
        assert 'generated_at' in data
        
        # Check user profile structure
        profile = data['user_profile']
        assert 'total_income' in profile
        assert 'total_expenses' in profile
        assert 'savings_rate' in profile
        assert 'categories_count' in profile
        assert 'overspending_categories' in profile
        
        # Check recommendations structure
        if data['recommendations']:
            recommendation = data['recommendations'][0]
            assert 'methodology_type' in recommendation
            assert 'reason' in recommendation
            assert 'confidence' in recommendation
            assert 'best_for' in recommendation
    
    def test_error_handling(self):
        """Test error handling for various edge cases"""
        # Non-existent methodology
        response = self.client.get('/api/budget/methodologies/99999/calculate')
        assert response.status_code == 404
        
        # Invalid request data
        response = self.client.post('/api/budget/methodologies/compare',
                                  json={'invalid': 'data'})
        assert response.status_code == 400
        
        # Empty methodology comparison
        response = self.client.post('/api/budget/methodologies/compare',
                                  json={'methodology_ids': []})
        assert response.status_code == 400
        
        # Too many methodologies to compare
        response = self.client.post('/api/budget/methodologies/compare',
                                  json={'methodology_ids': [1, 2, 3, 4, 5, 6]})
        assert response.status_code == 400


class TestBudgetMethodologyIntegration:
    """Test integration with existing budget system"""
    
    def setup_method(self):
        """Set up test environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self.create_integration_test_data()
    
    def teardown_method(self):
        """Clean up test environment"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def create_integration_test_data(self):
        """Create test data for integration tests"""
        # Create categories with different priorities
        categories = [
            Category(name='Housing', type='expense', budget_priority='critical'),
            Category(name='Food', type='expense', budget_priority='essential'),
            Category(name='Transportation', type='expense', budget_priority='essential'),
            Category(name='Entertainment', type='expense', budget_priority='discretionary'),
            Category(name='Shopping', type='expense', budget_priority='important'),
            Category(name='Salary', type='income')
        ]
        
        for cat in categories:
            db.session.add(cat)
        
        # Create income transaction
        income_transaction = Transaction(
            date=date.today(),
            amount=5000,
            category_id=6,  # Salary category
            type='income',
            description='Monthly salary'
        )
        db.session.add(income_transaction)
        
        # Create methodology
        methodology = BudgetMethodology(
            name='Integration Test Method',
            methodology_type='zero_based',
            is_active=True
        )
        db.session.add(methodology)
        
        db.session.commit()
    
    def test_end_to_end_methodology_workflow(self):
        """Test complete methodology workflow"""
        # 1. Get methodology recommendations
        response = self.client.get('/api/budget/methodologies/recommendations')
        assert response.status_code == 200
        recommendations = response.get_json()['recommendations']
        
        # 2. Get all available methodologies
        response = self.client.get('/api/budget/methodologies')
        assert response.status_code == 200
        methodologies = response.get_json()
        
        # 3. Calculate budget using active methodology
        active_methodology = next(m for m in methodologies if m['is_active'])
        response = self.client.post(f'/api/budget/methodologies/{active_methodology["id"]}/calculate',
                                  json={'total_income': 5000.0})
        assert response.status_code == 200
        calculation = response.get_json()['calculation_result']
        
        # 4. Apply methodology to update category budgets
        response = self.client.post(f'/api/budget/methodologies/{active_methodology["id"]}/apply',
                                  json={'total_income': 5000.0, 'auto_update': True})
        assert response.status_code == 200
        
        # 5. Verify budget was updated
        response = self.client.get('/api/categories')
        assert response.status_code == 200
        categories = response.get_json()
        
        # Check that expense categories now have budget limits
        expense_categories = [c for c in categories if c['type'] == 'expense']
        for category in expense_categories:
            if category['budget_limit']:
                assert category['budget_limit'] > 0
        
        # 6. Get budget progress to see applied methodology
        response = self.client.get('/api/budget/progress')
        assert response.status_code == 200
        budget_progress = response.get_json()
        
        # Verify we have budget progress data
        assert 'progress' in budget_progress
        assert 'summary' in budget_progress


if __name__ == '__main__':
    pytest.main([__file__])
