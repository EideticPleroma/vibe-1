#!/usr/bin/env python3
"""
Migration script for Budget Methodology System (Feature 1005)

This script creates the necessary database tables and seeds default methodology data.
Run this script to set up the budget methodology feature.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import BudgetMethodology
import json

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully")

def seed_default_methodologies():
    """Seed the database with default budget methodologies"""
    print("Seeding default budget methodologies...")
    
    with app.app_context():
        # Check if methodologies already exist
        if BudgetMethodology.query.first():
            print("⚠ Budget methodologies already exist. Skipping seed data.")
            return
        
        methodologies = [
            {
                'name': 'Zero-Based Budgeting',
                'description': 'Every dollar is assigned a specific purpose. Start from zero and justify every expense based on priority.',
                'methodology_type': 'zero_based',
                'is_active': True,  # Set as default active methodology
                'is_default': True,
                'configuration': {}
            },
            {
                'name': '50/30/20 Rule',
                'description': 'Allocate 50% for needs, 30% for wants, and 20% for savings and debt repayment.',
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
                'name': '60/20/20 Conservative Rule',
                'description': 'More conservative approach: 60% for needs, 20% for wants, 20% for savings.',
                'methodology_type': 'percentage_based',
                'is_active': False,
                'is_default': False,
                'configuration': {
                    'needs_percentage': 60,
                    'wants_percentage': 20,
                    'savings_percentage': 20
                }
            },
            {
                'name': '70/20/10 Relaxed Rule',
                'description': 'More relaxed approach: 70% for needs, 20% for wants, 10% for savings.',
                'methodology_type': 'percentage_based',
                'is_active': False,
                'is_default': False,
                'configuration': {
                    'needs_percentage': 70,
                    'wants_percentage': 20,
                    'savings_percentage': 10
                }
            },
            {
                'name': 'Envelope Budgeting',
                'description': 'Allocate specific amounts to spending "envelopes" for each category. Strict spending limits.',
                'methodology_type': 'envelope',
                'is_active': False,
                'is_default': False,
                'configuration': {
                    'allow_envelope_transfer': False,
                    'rollover_unused': True
                }
            },
            {
                'name': 'Flexible Envelope System',
                'description': 'Envelope budgeting with flexibility to transfer between categories when needed.',
                'methodology_type': 'envelope',
                'is_active': False,
                'is_default': False,
                'configuration': {
                    'allow_envelope_transfer': True,
                    'rollover_unused': True,
                    'max_transfer_percentage': 20
                }
            }
        ]
        
        for methodology_data in methodologies:
            methodology = BudgetMethodology(
                name=methodology_data['name'],
                description=methodology_data['description'],
                methodology_type=methodology_data['methodology_type'],
                is_active=methodology_data['is_active'],
                is_default=methodology_data['is_default']
            )
            
            if methodology_data['configuration']:
                methodology.set_configuration(methodology_data['configuration'])
            
            db.session.add(methodology)
            print(f"✓ Added methodology: {methodology_data['name']}")
        
        db.session.commit()
        print("✓ Default budget methodologies seeded successfully")

def verify_migration():
    """Verify that the migration was successful"""
    print("Verifying migration...")
    
    with app.app_context():
        # Check table creation
        try:
            methodology_count = BudgetMethodology.query.count()
            print(f"✓ BudgetMethodology table created with {methodology_count} records")
            
            # Check for active methodology
            active_methodology = BudgetMethodology.query.filter_by(is_active=True).first()
            if active_methodology:
                print(f"✓ Active methodology: {active_methodology.name}")
            else:
                print("⚠ No active methodology found")
            
            # Check methodology types
            types = [m.methodology_type for m in BudgetMethodology.query.all()]
            expected_types = ['zero_based', 'percentage_based', 'envelope']
            for expected_type in expected_types:
                if expected_type in types:
                    print(f"✓ Found methodology type: {expected_type}")
                else:
                    print(f"⚠ Missing methodology type: {expected_type}")
            
            print("✓ Migration verification completed successfully")
            
        except Exception as e:
            print(f"✗ Migration verification failed: {str(e)}")
            return False
    
    return True

def main():
    """Main migration function"""
    print("=== Budget Methodology System Migration (Feature 1005) ===")
    print("This will create the budget methodology tables and seed default data.")
    print()
    
    try:
        # Step 1: Create tables
        create_tables()
        print()
        
        # Step 2: Seed default data
        seed_default_methodologies()
        print()
        
        # Step 3: Verify migration
        if verify_migration():
            print()
            print("🎉 Migration completed successfully!")
            print("The Budget Methodology system is now ready to use.")
            print()
            print("Available methodologies:")
            with app.app_context():
                methodologies = BudgetMethodology.query.all()
                for methodology in methodologies:
                    status = "ACTIVE" if methodology.is_active else "inactive"
                    print(f"  - {methodology.name} ({methodology.methodology_type}) [{status}]")
        else:
            print("✗ Migration verification failed. Please check the errors above.")
            return 1
            
    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
