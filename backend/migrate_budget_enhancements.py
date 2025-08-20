#!/usr/bin/env python3
"""
Database migration script to add enhanced budget fields to categories table.
This script adds the new columns required for Feature 1001: Enhanced Budget Planning.

Run this script after updating the Category model in models.py.
"""

import sqlite3
import os
from datetime import datetime

def migrate_budget_enhancements():
    """Add enhanced budget fields to the categories table"""

    # Database path - adjust if your database is in a different location
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'finance_app.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Please ensure your database exists before running this migration.")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the new columns already exist
        cursor.execute("PRAGMA table_info(categories)")
        columns = [column[1] for column in cursor.fetchall()]

        new_columns = {
            'budget_period': "TEXT DEFAULT 'monthly'",
            'budget_type': "TEXT DEFAULT 'fixed'",
            'budget_priority': "TEXT DEFAULT 'essential'",
            'budget_percentage': "DECIMAL(5,2)",
            'budget_rolling_months': "INTEGER DEFAULT 3"
        }

        migrations_applied = 0

        for column_name, column_definition in new_columns.items():
            if column_name not in columns:
                print(f"Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE categories ADD COLUMN {column_name} {column_definition}")
                migrations_applied += 1
            else:
                print(f"Column {column_name} already exists - skipping")

        conn.commit()

        if migrations_applied > 0:
            print(f"\n✅ Migration completed! Added {migrations_applied} new columns to categories table.")
            print("The following columns were added:")
            for column in new_columns.keys():
                if column not in [c for c in columns]:
                    print(f"  - {column}")
        else:
            print("\n✅ No migrations needed - all columns already exist.")

        # Verify the migration
        cursor.execute("PRAGMA table_info(categories)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"\n📊 Categories table now has {len(updated_columns)} columns:")
        for column in updated_columns:
            print(f"  - {column}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🔄 Starting database migration for enhanced budget features...")
    print("This will add new columns to support flexible budgeting (Feature 1001)")

    success = migrate_budget_enhancements()

    if success:
        print("\n🎉 Migration successful!")
        print("\nYou can now use the enhanced budget features:")
        print("- Flexible budget periods (daily, weekly, monthly, yearly)")
        print("- Multiple budget types (fixed, percentage, rolling average)")
        print("- Priority-based budgeting (critical, essential, important, discretionary)")
        print("- Automated budget suggestions")
        print("- Budget template copying with inflation adjustments")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        exit(1)
