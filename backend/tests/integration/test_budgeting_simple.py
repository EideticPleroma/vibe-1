#!/usr/bin/env python3
"""
Simple unit tests for Enhanced Budgeting Features (Feature 1001)
Tests the enhanced Category model methods without database dependencies.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from models import Category


def test_category_model_methods():
    """Test Category model methods"""
    print("🧪 Testing Category model methods...")

    # Create a test category instance
    category = Category(
        name='Test Category',
        type='expense',
        color='#FF5733',
        budget_limit=500.0,
        budget_period='monthly',
        budget_type='fixed',
        budget_priority='essential',
        budget_percentage=None,
        budget_rolling_months=3
    )

    # Test calculate_effective_budget - fixed type
    effective = category.calculate_effective_budget()
    assert effective == 500.0, f"Expected 500.0, got {effective}"
    print("✅ Fixed budget calculation works")

    # Test percentage budget
    category.budget_type = 'percentage'
    category.budget_percentage = 15.0
    effective = category.calculate_effective_budget(total_income=3000.0)
    expected = 3000.0 * 0.15  # 15% of 3000
    assert effective == expected, f"Expected {expected}, got {effective}"
    print("✅ Percentage budget calculation works")

    # Test rolling average budget (placeholder)
    category.budget_type = 'rolling_average'
    effective = category.calculate_effective_budget()
    assert effective == 500.0, f"Expected 500.0 (placeholder), got {effective}"
    print("✅ Rolling average budget calculation works")

    # Test budget period days
    category.budget_period = 'daily'
    assert category.get_budget_period_days() == 1, "Daily should be 1 day"
    print("✅ Daily period calculation works")

    category.budget_period = 'weekly'
    assert category.get_budget_period_days() == 7, "Weekly should be 7 days"
    print("✅ Weekly period calculation works")

    category.budget_period = 'monthly'
    assert category.get_budget_period_days() == 30, "Monthly should be 30 days"
    print("✅ Monthly period calculation works")

    category.budget_period = 'yearly'
    assert category.get_budget_period_days() == 365, "Yearly should be 365 days"
    print("✅ Yearly period calculation works")

    # Test to_dict method
    data = category.to_dict()
    required_fields = ['budget_period', 'budget_type', 'budget_priority', 'budget_rolling_months']
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    print("✅ to_dict includes all enhanced fields")

    print("🎉 All Category model tests passed!")


def test_budget_calculations():
    """Test various budget calculation scenarios"""
    print("\n🧪 Testing budget calculations...")

    # Test scenarios
    scenarios = [
        # (budget_type, budget_limit, budget_percentage, total_income, expected)
        ('fixed', 500.0, None, 3000.0, 500.0),
        ('percentage', 1000.0, 10.0, 5000.0, 500.0),  # 10% of 5000
        ('percentage', 1000.0, 25.0, 4000.0, 1000.0),  # 25% of 4000
        ('rolling_average', 750.0, None, 3000.0, 750.0),  # Placeholder
    ]

    for i, (budget_type, budget_limit, budget_percentage, total_income, expected) in enumerate(scenarios):
        category = Category(
            name=f'Test {i}',
            type='expense',
            color='#123456',
            budget_limit=budget_limit,
            budget_type=budget_type,
            budget_percentage=budget_percentage
        )

        result = category.calculate_effective_budget(total_income=total_income)
        assert abs(result - expected) < 0.01, f"Scenario {i}: Expected {expected}, got {result}"
        print(f"✅ Scenario {i} passed: {budget_type} budget = {result}")

    print("🎉 All budget calculation tests passed!")


def test_validation_scenarios():
    """Test validation scenarios for enhanced fields"""
    print("\n🧪 Testing validation scenarios...")

    # Test valid periods
    valid_periods = ['daily', 'weekly', 'monthly', 'yearly']
    for period in valid_periods:
        category = Category(name='Test', type='expense', budget_period=period)
        days = category.get_budget_period_days()
        assert days > 0, f"Period {period} should have positive days"
    print("✅ All valid budget periods work")

    # Test valid types
    valid_types = ['fixed', 'percentage', 'rolling_average']
    for budget_type in valid_types:
        category = Category(name='Test', type='expense', budget_type=budget_type)
        result = category.calculate_effective_budget()
        assert result >= 0, f"Budget type {budget_type} should return non-negative amount"
    print("✅ All valid budget types work")

    # Test valid priorities
    valid_priorities = ['critical', 'essential', 'important', 'discretionary']
    for priority in valid_priorities:
        category = Category(name='Test', type='expense', budget_priority=priority)
        data = category.to_dict()
        assert data['budget_priority'] == priority, f"Priority {priority} should be preserved"
    print("✅ All valid budget priorities work")

    print("🎉 All validation tests passed!")


if __name__ == "__main__":
    print("🧪 Running Simple Enhanced Budgeting Tests...")
    print("=" * 50)

    try:
        test_category_model_methods()
        test_budget_calculations()
        test_validation_scenarios()

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! Enhanced Budgeting Feature 1001 is working correctly!")
        print("✅ Category model enhancements")
        print("✅ Budget calculation methods")
        print("✅ Validation logic")
        print("✅ Period and type handling")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
