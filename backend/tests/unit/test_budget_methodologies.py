"""
Unit tests for Budget Methodology models and calculation engines (Feature 1005)
"""

import pytest
import json
from datetime import date, datetime, timezone
from unittest.mock import patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models import (
    db, BudgetMethodology, Category, Transaction,
    BudgetMethodologyEngine, ZeroBasedBudgetEngine, 
    PercentageBasedBudgetEngine, EnvelopeBudgetEngine,
    BudgetMethodologyFactory, get_active_methodology,
    set_active_methodology, calculate_methodology_budget,
    apply_methodology_to_categories
)
from app import app


class TestBudgetMethodologyModel:
    """Test cases for BudgetMethodology model"""
    
    def setup_method(self):
        """Set up test database"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
    
    def teardown_method(self):
        """Clean up test database"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_budget_methodology_creation(self):
        """Test creating a budget methodology"""
        with self.app.app_context():
            methodology = BudgetMethodology(
                name='Test Zero-Based',
                description='Test methodology',
                methodology_type='zero_based',
                is_active=True,
                is_default=True
            )
            
            db.session.add(methodology)
            db.session.commit()
            
            # Test retrieval
            retrieved = BudgetMethodology.query.filter_by(name='Test Zero-Based').first()
            assert retrieved is not None
            assert retrieved.methodology_type == 'zero_based'
            assert retrieved.is_active is True
            assert retrieved.is_default is True
    
    def test_configuration_methods(self):
        """Test configuration get/set methods"""
        with self.app.app_context():
            methodology = BudgetMethodology(
                name='Test Percentage',
                methodology_type='percentage_based'
            )
            
            # Test setting configuration
            config = {
                'needs_percentage': 50,
                'wants_percentage': 30,
                'savings_percentage': 20
            }
            methodology.set_configuration(config)
            
            # Test getting configuration
            retrieved_config = methodology.get_configuration()
            assert retrieved_config == config
            
            # Test JSON storage
            assert methodology.configuration == json.dumps(config)
    
    def test_to_dict(self):
        """Test model serialization"""
        with self.app.app_context():
            methodology = BudgetMethodology(
                name='Test Envelope',
                description='Test envelope budgeting',
                methodology_type='envelope',
                is_active=False,
                is_default=False
            )
            methodology.set_configuration({'allow_envelope_transfer': True})
            
            db.session.add(methodology)
            db.session.commit()
            
            data = methodology.to_dict()
            
            assert data['name'] == 'Test Envelope'
            assert data['methodology_type'] == 'envelope'
            assert data['configuration']['allow_envelope_transfer'] is True
            assert 'created_at' in data
            assert 'updated_at' in data


class TestBudgetMethodologyEngines:
    """Test cases for methodology calculation engines"""
    
    def setup_method(self):
        """Set up test data"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
            
            # Create test categories
            self.categories = [
                Category(name='Rent', type='expense', budget_priority='critical'),
                Category(name='Groceries', type='expense', budget_priority='essential'),
                Category(name='Entertainment', type='expense', budget_priority='discretionary'),
                Category(name='Utilities', type='expense', budget_priority='essential'),
                Category(name='Shopping', type='expense', budget_priority='important')
            ]
            
            for cat in self.categories:
                db.session.add(cat)
            
            db.session.commit()
    
    def teardown_method(self):
        """Clean up test database"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_zero_based_engine(self):
        """Test Zero-Based budgeting engine"""
        with self.app.app_context():
            methodology = BudgetMethodology(
                name='Zero-Based Test',
                methodology_type='zero_based'
            )
            
            # Refresh categories to ensure they're bound to the current session
            categories = Category.query.all()
            
            engine = ZeroBasedBudgetEngine(methodology)
            result = engine.calculate_category_budgets(5000.0, categories)
            
            assert result['methodology'] == 'Zero-Based Budgeting'
            assert result['total_income'] == 5000.0
            assert len(result['allocations']) == len(self.categories)
            assert result['total_allocated'] + result['unallocated'] == 5000.0
            
            # Test priority ordering (critical categories should come first)
            allocations = result['allocations']
            first_allocation = allocations[0]
            assert first_allocation['priority'] == 'critical'
    
    def test_percentage_based_engine(self):
        """Test 50/30/20 percentage-based budgeting engine"""
        with self.app.app_context():
            methodology = BudgetMethodology(
                name='50/30/20 Test',
                methodology_type='percentage_based'
            )
            methodology.set_configuration({
                'needs_percentage': 50,
                'wants_percentage': 30,
                'savings_percentage': 20
            })
            
            # Refresh categories to ensure they're bound to the current session
            categories = Category.query.all()
            
            engine = PercentageBasedBudgetEngine(methodology)
            result = engine.calculate_category_budgets(5000.0, categories)
            
            assert '50/30/20' in result['methodology']
            assert result['total_income'] == 5000.0
            
            # Test category breakdown
            breakdown = result['category_breakdown']
            assert breakdown['needs']['budget'] == 2500.0  # 50% of 5000
            assert breakdown['wants']['budget'] == 1500.0  # 30% of 5000
            assert breakdown['savings']['budget'] == 1000.0  # 20% of 5000
            
            # Test that all categories are assigned to a type
            total_categories = (len(breakdown['needs']['categories']) + 
                              len(breakdown['wants']['categories']) + 
                              len(breakdown['savings']['categories']))
            assert total_categories == len(self.categories)
    
    def test_envelope_engine(self):
        """Test Envelope budgeting engine"""
        with self.app.app_context():
            methodology = BudgetMethodology(
                name='Envelope Test',
                methodology_type='envelope'
            )
            methodology.set_configuration({
                'allow_envelope_transfer': False,
                'rollover_unused': True
            })
            
            # Refresh categories to ensure they're bound to the current session
            categories = Category.query.all()
            
            engine = EnvelopeBudgetEngine(methodology)
            result = engine.calculate_category_budgets(5000.0, categories)
            
            assert result['methodology'] == 'Envelope Budgeting'
            assert result['total_income'] == 5000.0
            assert len(result['envelopes']) == len(self.categories)
            
            # Test envelope allocation
            envelopes = result['envelopes']
            for envelope in envelopes:
                assert envelope['envelope_amount'] > 0
                assert envelope['percentage_of_income'] > 0
                assert envelope['envelope_status'] == 'active'
    
    def test_methodology_factory(self):
        """Test BudgetMethodologyFactory"""
        with self.app.app_context():
            # Test creating different engines
            zero_methodology = BudgetMethodology(
                name='Zero-Based',
                methodology_type='zero_based'
            )
            zero_engine = BudgetMethodologyFactory.create_engine(zero_methodology)
            assert isinstance(zero_engine, ZeroBasedBudgetEngine)
            
            percentage_methodology = BudgetMethodology(
                name='Percentage',
                methodology_type='percentage_based'
            )
            percentage_engine = BudgetMethodologyFactory.create_engine(percentage_methodology)
            assert isinstance(percentage_engine, PercentageBasedBudgetEngine)
            
            envelope_methodology = BudgetMethodology(
                name='Envelope',
                methodology_type='envelope'
            )
            envelope_engine = BudgetMethodologyFactory.create_engine(envelope_methodology)
            assert isinstance(envelope_engine, EnvelopeBudgetEngine)
            
            # Test unknown methodology type
            unknown_methodology = BudgetMethodology(
                name='Unknown',
                methodology_type='unknown_type'
            )
            
            with pytest.raises(ValueError, match="Unknown methodology type"):
                BudgetMethodologyFactory.create_engine(unknown_methodology)


class TestBudgetMethodologyUtilities:
    """Test cases for utility functions"""
    
    def setup_method(self):
        """Set up test data"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
    
    def teardown_method(self):
        """Clean up test database"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_active_methodology_management(self):
        """Test get/set active methodology functions"""
        with self.app.app_context():
            # Initially no active methodology
            assert get_active_methodology() is None
            
            # Create methodologies
            methodology1 = BudgetMethodology(
                name='Method 1',
                methodology_type='zero_based',
                is_active=False
            )
            methodology2 = BudgetMethodology(
                name='Method 2',
                methodology_type='percentage_based',
                is_active=False
            )
            
            db.session.add(methodology1)
            db.session.add(methodology2)
            db.session.commit()
            
            # Set active methodology
            active = set_active_methodology(methodology1.id)
            assert active is not None
            assert active.id == methodology1.id
            assert active.is_active is True
            
            # Verify only one is active
            all_methodologies = BudgetMethodology.query.all()
            active_count = sum(1 for m in all_methodologies if m.is_active)
            assert active_count == 1
            
            # Get active methodology
            retrieved_active = get_active_methodology()
            assert retrieved_active.id == methodology1.id
            
            # Change active methodology
            new_active = set_active_methodology(methodology2.id)
            assert new_active.id == methodology2.id
            
            # Verify previous is no longer active
            methodology1_updated = db.session.get(BudgetMethodology, methodology1.id)
            assert methodology1_updated.is_active is False
    
    @patch('models.get_total_income')
    def test_calculate_methodology_budget(self, mock_get_income):
        """Test calculate_methodology_budget function"""
        with self.app.app_context():
            mock_get_income.return_value = 5000.0
            
            # Create methodology and categories
            methodology = BudgetMethodology(
                name='Test Method',
                methodology_type='zero_based'
            )
            db.session.add(methodology)
            
            category = Category(name='Test Category', type='expense', budget_priority='essential')
            db.session.add(category)
            db.session.commit()
            
            # Test calculation
            result = calculate_methodology_budget(methodology.id)
            
            assert result['methodology'] == 'Zero-Based Budgeting'
            assert result['total_income'] == 5000.0
            
            # Test with provided income
            result_with_income = calculate_methodology_budget(methodology.id, 6000.0)
            assert result_with_income['total_income'] == 6000.0
            
            # Test with non-existent methodology
            with pytest.raises(ValueError, match="not found"):
                calculate_methodology_budget(99999)
    
    @patch('models.get_total_income')
    def test_apply_methodology_to_categories(self, mock_get_income):
        """Test apply_methodology_to_categories function"""
        with self.app.app_context():
            mock_get_income.return_value = 5000.0
            
            # Create methodology and categories
            methodology = BudgetMethodology(
                name='Test Method',
                methodology_type='zero_based'
            )
            db.session.add(methodology)
            
            category = Category(
                name='Test Category', 
                type='expense', 
                budget_priority='essential',
                budget_limit=0.0  # No initial budget
            )
            db.session.add(category)
            db.session.commit()
            
            # Test application without auto-update
            result = apply_methodology_to_categories(methodology.id, auto_update=False)
            
            # Budget should not be updated
            category_updated = db.session.get(Category, category.id)
            assert category_updated.budget_limit == 0.0
            
            # Test application with auto-update
            result = apply_methodology_to_categories(methodology.id, auto_update=True)
            
            # Budget should be updated
            category_updated = db.session.get(Category, category.id)
            assert category_updated.budget_limit > 0


class TestBudgetMethodologyValidation:
    """Test cases for methodology validation"""
    
    def setup_method(self):
        """Set up test data"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
    
    def teardown_method(self):
        """Clean up test database"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_percentage_based_validation(self):
        """Test validation for percentage-based methodology"""
        with self.app.app_context():
            # Valid configuration
            methodology = BudgetMethodology(
                name='Valid Percentage',
                methodology_type='percentage_based'
            )
            methodology.set_configuration({
                'needs_percentage': 50,
                'wants_percentage': 30,
                'savings_percentage': 20
            })
            
            engine = PercentageBasedBudgetEngine(methodology)
            is_valid, error_message = engine.validate_configuration()
            assert is_valid is True
            assert error_message is None
    
    def test_zero_based_validation(self):
        """Test validation for zero-based methodology"""
        with self.app.app_context():
            methodology = BudgetMethodology(
                name='Zero-Based',
                methodology_type='zero_based'
            )
            
            engine = ZeroBasedBudgetEngine(methodology)
            is_valid, error_message = engine.validate_configuration()
            assert is_valid is True
            assert error_message is None
    
    def test_envelope_validation(self):
        """Test validation for envelope methodology"""
        with self.app.app_context():
            methodology = BudgetMethodology(
                name='Envelope',
                methodology_type='envelope'
            )
            methodology.set_configuration({
                'allow_envelope_transfer': True,
                'rollover_unused': True
            })
            
            engine = EnvelopeBudgetEngine(methodology)
            is_valid, error_message = engine.validate_configuration()
            assert is_valid is True
            assert error_message is None


if __name__ == '__main__':
    pytest.main([__file__])
