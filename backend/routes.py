"""
API routes for Personal Finance App
Provides RESTful endpoints for categories, transactions, and investments
"""

from flask import Blueprint, request, jsonify
from models import (
    db, Category, Transaction, Investment, BudgetMethodology,
    get_total_income, get_total_expenses, get_net_income,
    get_total_investment_value, get_total_investment_gain_loss,
    get_budget_progress_advanced, get_budget_historical_trends,
    get_transaction_budget_impact, get_budget_performance_score,
    get_active_methodology, set_active_methodology, calculate_methodology_budget,
    apply_methodology_to_categories, BudgetMethodologyFactory
)
from datetime import datetime, date
from sqlalchemy import desc, func
import json

# Create blueprint for API routes
api = Blueprint('api', __name__, url_prefix='/api')

# Error handling helper
def handle_error(message, status_code=400):
    return jsonify({'error': message}), status_code

# ============================================================================
# CATEGORY ROUTES
# ============================================================================

@api.route('/categories', methods=['GET'])
def get_categories():
    """Get all budget categories"""
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories])
    except Exception as e:
        return handle_error(f"Error fetching categories: {str(e)}", 500)

@api.route('/categories', methods=['POST'])
def create_category():
    """Create a new budget category"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'name' not in data or 'type' not in data:
            return handle_error("Name and type are required fields")
        
        if data['type'] not in ['income', 'expense']:
            return handle_error("Type must be 'income' or 'expense'")
        
        # Check if category already exists
        existing = Category.query.filter_by(name=data['name']).first()
        if existing:
            return handle_error("Category with this name already exists")
        
        # Enhanced budget validation (Feature 1001)
        if any(key in data for key in ['budget_limit', 'budget_period', 'budget_type', 'budget_priority']):
            if data['type'] != 'expense':
                return handle_error("Budget settings can only be configured for expense categories")

            # Validate budget_limit
            if 'budget_limit' in data:
                try:
                    budget = float(data['budget_limit'])
                    if budget < 0:
                        return handle_error("Budget limit must be non-negative")
                except ValueError:
                    return handle_error("Invalid budget limit value")

            # Validate budget_period
            if 'budget_period' in data:
                valid_periods = ['daily', 'weekly', 'monthly', 'yearly']
                if data['budget_period'] not in valid_periods:
                    return handle_error(f"Budget period must be one of: {', '.join(valid_periods)}")

            # Validate budget_type
            if 'budget_type' in data:
                valid_types = ['fixed', 'percentage', 'rolling_average']
                if data['budget_type'] not in valid_types:
                    return handle_error(f"Budget type must be one of: {', '.join(valid_types)}")

                # Validate percentage for percentage-based budgets
                if data['budget_type'] == 'percentage':
                    if 'budget_percentage' not in data or not data['budget_percentage']:
                        return handle_error("budget_percentage is required for percentage-based budgets")
                    try:
                        percentage = float(data['budget_percentage'])
                        if not 0 < percentage <= 100:
                            return handle_error("Budget percentage must be between 0 and 100")
                    except ValueError:
                        return handle_error("Invalid budget percentage value")

            # Validate budget_priority
            if 'budget_priority' in data:
                valid_priorities = ['critical', 'essential', 'important', 'discretionary']
                if data['budget_priority'] not in valid_priorities:
                    return handle_error(f"Budget priority must be one of: {', '.join(valid_priorities)}")

            # Validate rolling months
            if 'budget_rolling_months' in data:
                try:
                    months = int(data['budget_rolling_months'])
                    if not 1 <= months <= 12:
                        return handle_error("Budget rolling months must be between 1 and 12")
                except ValueError:
                    return handle_error("Invalid budget rolling months value")

        # Create new category with enhanced budget fields
        category = Category(
            name=data['name'],
            type=data['type'],
            color=data.get('color', '#007bff'),
            budget_limit=float(data.get('budget_limit', 0.0)) if data.get('budget_limit') else None,
            budget_period=data.get('budget_period', 'monthly'),
            budget_type=data.get('budget_type', 'fixed'),
            budget_priority=data.get('budget_priority', 'essential'),
            budget_percentage=float(data.get('budget_percentage', 0.0)) if data.get('budget_percentage') else None,
            budget_rolling_months=data.get('budget_rolling_months', 3)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify(category.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error creating category: {str(e)}", 500)

@api.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update an existing budget category"""
    try:
        category = db.session.get(Category, category_id)
        if category is None:
            return handle_error("Category not found", 404)
        data = request.get_json()
        
        if 'name' in data:
            # Check if new name conflicts with existing category
            existing = Category.query.filter_by(name=data['name']).first()
            if existing and existing.id != category_id:
                return handle_error("Category with this name already exists")
            category.name = data['name']
        
        if 'type' in data:
            if data['type'] not in ['income', 'expense']:
                return handle_error("Type must be 'income' or 'expense'")
            category.type = data['type']

        # Enhanced budget field updates (Feature 1001)
        if any(key in data for key in ['budget_limit', 'budget_period', 'budget_type', 'budget_priority']):
            if category.type != 'expense':
                return handle_error("Budget settings can only be configured for expense categories")

            # Validate budget_limit
            if 'budget_limit' in data:
                try:
                    budget = float(data['budget_limit'])
                    if budget < 0:
                        return handle_error("Budget limit must be non-negative")
                    category.budget_limit = budget
                except ValueError:
                    return handle_error("Invalid budget limit value")

            # Validate and update budget_period
            if 'budget_period' in data:
                valid_periods = ['daily', 'weekly', 'monthly', 'yearly']
                if data['budget_period'] not in valid_periods:
                    return handle_error(f"Budget period must be one of: {', '.join(valid_periods)}")
                category.budget_period = data['budget_period']

            # Validate and update budget_type
            if 'budget_type' in data:
                valid_types = ['fixed', 'percentage', 'rolling_average']
                if data['budget_type'] not in valid_types:
                    return handle_error(f"Budget type must be one of: {', '.join(valid_types)}")
                category.budget_type = data['budget_type']

                # Validate percentage for percentage-based budgets
                if data['budget_type'] == 'percentage':
                    if 'budget_percentage' not in data or not data['budget_percentage']:
                        return handle_error("budget_percentage is required for percentage-based budgets")
                    try:
                        percentage = float(data['budget_percentage'])
                        if not 0 < percentage <= 100:
                            return handle_error("Budget percentage must be between 0 and 100")
                        category.budget_percentage = percentage
                    except ValueError:
                        return handle_error("Invalid budget percentage value")

            # Validate and update budget_priority
            if 'budget_priority' in data:
                valid_priorities = ['critical', 'essential', 'important', 'discretionary']
                if data['budget_priority'] not in valid_priorities:
                    return handle_error(f"Budget priority must be one of: {', '.join(valid_priorities)}")
                category.budget_priority = data['budget_priority']

            # Validate and update rolling months
            if 'budget_rolling_months' in data:
                try:
                    months = int(data['budget_rolling_months'])
                    if not 1 <= months <= 12:
                        return handle_error("Budget rolling months must be between 1 and 12")
                    category.budget_rolling_months = months
                except ValueError:
                    return handle_error("Invalid budget rolling months value")
        
        if 'color' in data:
            category.color = data['color']
        
        db.session.commit()
        return jsonify(category.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error updating category: {str(e)}", 500)

@api.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a budget category"""
    try:
        category = db.session.get(Category, category_id)
        if category is None:
            return handle_error("Category not found", 404)
        
        # Check if category has transactions
        if category.transactions:
            return handle_error("Cannot delete category with existing transactions", 400)
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'message': 'Category deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error deleting category: {str(e)}", 500)

# ============================================================================
# TRANSACTION ROUTES
# ============================================================================

@api.route('/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions with optional filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        category_id = request.args.get('category_id', type=int)
        transaction_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Transaction.query
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if transaction_type:
            if transaction_type not in ['income', 'expense']:
                return handle_error("Type must be 'income' or 'expense'")
            query = query.filter_by(type=transaction_type)
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Transaction.date >= start_date)
            except ValueError:
                return handle_error("Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Transaction.date <= end_date)
            except ValueError:
                return handle_error("Invalid end_date format. Use YYYY-MM-DD")
        
        # Order by date (newest first)
        query = query.order_by(desc(Transaction.date))
        
        # Paginate results
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        transactions = pagination.items
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return handle_error(f"Error fetching transactions: {str(e)}", 500)

@api.route('/transactions', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'category_id', 'type']
        for field in required_fields:
            if field not in data:
                return handle_error(f"Missing required field: {field}")
        
        if data['type'] not in ['income', 'expense']:
            return handle_error("Type must be 'income' or 'expense'")
        
        # Validate category exists
        category = db.session.get(Category, data['category_id'])
        if not category:
            return handle_error("Invalid category_id")
        
        # Validate amount
        try:
            amount = float(data['amount'])
            if amount == 0:
                return handle_error("Amount cannot be zero")
        except ValueError:
            return handle_error("Invalid amount value")
        
        # Create transaction
        transaction = Transaction(
            date=datetime.strptime(data['date'], '%Y-%m-%d').date() if 'date' in data else date.today(),
            amount=amount if data['type'] == 'income' else -abs(amount),
            category_id=data['category_id'],
            description=data.get('description', ''),
            type=data['type']
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify(transaction.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error creating transaction: {str(e)}", 500)

@api.route('/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """Update an existing transaction"""
    try:
        transaction = db.session.get(Transaction, transaction_id)
        if transaction is None:
            return handle_error("Transaction not found", 404)
        data = request.get_json()
        
        if 'date' in data:
            try:
                transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return handle_error("Invalid date format. Use YYYY-MM-DD")
        
        if 'amount' in data:
            try:
                amount = float(data['amount'])
                if amount == 0:
                    return handle_error("Amount cannot be zero")
                transaction.amount = amount if transaction.type == 'income' else -abs(amount)
            except ValueError:
                return handle_error("Invalid amount value")
        
        if 'category_id' in data:
            category = db.session.get(Category, data['category_id'])
            if not category:
                return handle_error("Invalid category_id")
            transaction.category_id = data['category_id']
        
        if 'description' in data:
            transaction.description = data['description']
        
        if 'type' in data:
            if data['type'] not in ['income', 'expense']:
                return handle_error("Type must be 'income' or 'expense'")
            transaction.type = data['type']
            # Adjust amount sign based on new type
            if transaction.type == 'income':
                transaction.amount = abs(transaction.amount)
            else:
                transaction.amount = -abs(transaction.amount)
        
        db.session.commit()
        return jsonify(transaction.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error updating transaction: {str(e)}", 500)

@api.route('/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete a transaction"""
    try:
        transaction = db.session.get(Transaction, transaction_id)
        if transaction is None:
            return handle_error("Transaction not found", 404)
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': 'Transaction deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error deleting transaction: {str(e)}", 500)

# ============================================================================
# INVESTMENT ROUTES
# ============================================================================

@api.route('/investments', methods=['GET'])
def get_investments():
    """Get all investment holdings"""
    try:
        investments = Investment.query.all()
        return jsonify([investment.to_dict() for investment in investments])
        
    except Exception as e:
        return handle_error(f"Error fetching investments: {str(e)}", 500)

@api.route('/investments', methods=['POST'])
def create_investment():
    """Create a new investment holding"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['asset_name', 'asset_type', 'quantity', 'purchase_price', 'purchase_date']
        for field in required_fields:
            if field not in data:
                return handle_error(f"Missing required field: {field}")
        
        # Validate numeric fields
        try:
            quantity = float(data['quantity'])
            purchase_price = float(data['purchase_price'])
            if quantity <= 0 or purchase_price <= 0:
                return handle_error("Quantity and purchase price must be positive")
        except ValueError:
            return handle_error("Invalid numeric values")
        
        # Validate date
        try:
            purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
        except ValueError:
            return handle_error("Invalid purchase_date format. Use YYYY-MM-DD")
        
        # Create investment (current_price defaults to purchase_price)
        investment = Investment(
            asset_name=data['asset_name'],
            asset_type=data['asset_type'],
            quantity=quantity,
            purchase_price=purchase_price,
            current_price=data.get('current_price', purchase_price),
            purchase_date=purchase_date
        )
        
        db.session.add(investment)
        db.session.commit()
        
        return jsonify(investment.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error creating investment: {str(e)}", 500)

@api.route('/investments/<int:investment_id>', methods=['PUT'])
def update_investment(investment_id):
    """Update an existing investment"""
    try:
        investment = db.session.get(Investment, investment_id)
        if investment is None:
            return handle_error("Investment not found", 404)
        data = request.get_json()
        
        if 'asset_name' in data:
            investment.asset_name = data['asset_name']
        
        if 'asset_type' in data:
            investment.asset_type = data['asset_type']
        
        if 'quantity' in data:
            try:
                quantity = float(data['quantity'])
                if quantity <= 0:
                    return handle_error("Quantity must be positive")
                investment.quantity = quantity
            except ValueError:
                return handle_error("Invalid quantity value")
        
        if 'purchase_price' in data:
            try:
                purchase_price = float(data['purchase_price'])
                if purchase_price <= 0:
                    return handle_error("Purchase price must be positive")
                investment.purchase_price = purchase_price
            except ValueError:
                return handle_error("Invalid purchase price value")
        
        if 'current_price' in data:
            try:
                current_price = float(data['current_price'])
                if current_price < 0:
                    return handle_error("Current price cannot be negative")
                investment.current_price = current_price
            except ValueError:
                return handle_error("Invalid current price value")
        
        if 'purchase_date' in data:
            try:
                purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
                investment.purchase_date = purchase_date
            except ValueError:
                return handle_error("Invalid purchase_date format. Use YYYY-MM-DD")
        
        db.session.commit()
        return jsonify(investment.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error updating investment: {str(e)}", 500)

@api.route('/investments/<int:investment_id>', methods=['DELETE'])
def delete_investment(investment_id):
    """Delete an investment holding"""
    try:
        investment = db.session.get(Investment, investment_id)
        if investment is None:
            return handle_error("Investment not found", 404)
        db.session.delete(investment)
        db.session.commit()
        
        return jsonify({'message': 'Investment deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error deleting investment: {str(e)}", 500)

# ============================================================================
# DASHBOARD & ANALYTICS ROUTES
# ============================================================================

@api.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard summary data"""
    try:
        # Get date range (default to current month)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return handle_error("Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return handle_error("Invalid end_date format. Use YYYY-MM-DD")
        
        # Calculate financial summary
        total_income = get_total_income(start_date, end_date)
        total_expenses = get_total_expenses(start_date, end_date)
        net_income = get_net_income(start_date, end_date)
        
        # Investment summary
        total_investment_value = get_total_investment_value()
        total_investment_gain_loss = get_total_investment_gain_loss()
        
        # Category breakdown for expenses
        expense_categories = db.session.query(
            Category.name,
            Category.color,
            func.sum(Transaction.amount).label('total')
        ).join(Transaction).filter(
            Transaction.type == 'expense'
        )

        if start_date:
            expense_categories = expense_categories.filter(Transaction.date >= start_date)
        if end_date:
            expense_categories = expense_categories.filter(Transaction.date <= end_date)

        expense_categories = expense_categories.group_by(Category.id, Category.name, Category.color).all()

        print(f"DEBUG: expense_categories: {expense_categories}")

        expense_breakdown = [
            {
                'name': cat.name,
                'color': cat.color,
                'total': float(abs(cat.total)) if cat.total is not None else 0.0
            }
            for cat in expense_categories
        ]
        
        # Recent transactions
        recent_transactions = Transaction.query.order_by(
            desc(Transaction.date)
        ).limit(5).all()
        
        # Budget progress
        budget_progress = []
        expense_categories_with_budget = Category.query.filter_by(type='expense').filter(Category.budget_limit > 0).all()
        for cat in expense_categories_with_budget:
            spent_query = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.category_id == cat.id,
                Transaction.type == 'expense'
            )
            if start_date:
                spent_query = spent_query.filter(Transaction.date >= start_date)
            if end_date:
                spent_query = spent_query.filter(Transaction.date <= end_date)
            spent = abs(float(spent_query.scalar() or 0))
            progress = {
                'category': cat.name,
                'budget': float(cat.budget_limit),
                'spent': spent,
                'percentage': (spent / float(cat.budget_limit) * 100) if cat.budget_limit and float(cat.budget_limit) > 0 else 0
            }
            budget_progress.append(progress)

        alerts = []
        warning_threshold = 0.8
        over_threshold = 1.0
        for progress in budget_progress:
            if progress['percentage'] > over_threshold * 100:
                alerts.append(f"Over budget in {progress['category']}: {progress['percentage']:.1f}% used")
            elif progress['percentage'] > warning_threshold * 100:
                alerts.append(f"Warning: Approaching budget in {progress['category']}: {progress['percentage']:.1f}% used")

        return jsonify({
            'financial_summary': {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_income': net_income
            },
            'investment_summary': {
                'total_value': total_investment_value,
                'total_gain_loss': total_investment_gain_loss
            },
            'expense_breakdown': expense_breakdown,
            'recent_transactions': [t.to_dict() for t in recent_transactions],
            'budget_progress': budget_progress,
            'alerts': alerts
        })
        
    except Exception as e:
        return handle_error(f"Error fetching dashboard data: {str(e)}", 500)

@api.route('/analytics/spending-trends', methods=['GET'])
def get_spending_trends():
    """Get spending trends over time"""
    try:
        # Get date range (default to last 6 months)
        months = request.args.get('months', 6, type=int)
        
        # Calculate date range
        end_date = date.today()
        start_date = date(end_date.year, max(1, end_date.month - months), 1)
        
        # Get monthly spending data
        monthly_data = db.session.query(
            func.strftime('%Y-%m', Transaction.date).label('month'),
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.type == 'expense',
            Transaction.amount < 0, # Only sum negative amounts for expenses
            Transaction.date >= start_date
        ).group_by('month').order_by('month').all()

        trends = [
            {
                'month': month,
                'total': float(abs(total)) if total is not None else 0.0 # Ensure positive spending values and handle None
            }
            for month, total in monthly_data
        ]
        
        return jsonify({
            'period': f'Last {months} months',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'trends': trends
        })
        
    except Exception as e:
        return handle_error(f"Error fetching spending trends: {str(e)}", 500)

@api.route('/analytics/investment-performance', methods=['GET'])
def get_investment_performance():
    """Get investment performance summary"""
    try:
        investments = Investment.query.all()
        
        performance_data = []
        for investment in investments:
            performance_data.append({
                'asset_name': investment.asset_name,
                'asset_type': investment.asset_type,
                'total_invested': investment.total_invested,
                'current_value': investment.current_value,
                'total_gain_loss': investment.total_gain_loss,
                'gain_loss_percentage': investment.gain_loss_percentage,
                'is_profitable': investment.is_profitable
            })
        
        # Sort by gain/loss percentage
        performance_data.sort(key=lambda x: x['gain_loss_percentage'], reverse=True)
        
        return jsonify({
            'total_investments': len(investments),
            'performance_data': performance_data
        })
        
    except Exception as e:
        return handle_error(f"Error fetching investment performance: {str(e)}", 500)

# ============================================================================
# ENHANCED BUDGET ENDPOINTS (Feature 1001)
# ============================================================================

@api.route('/budget/suggestions', methods=['GET'])
def get_budget_suggestions():
    """Get automated budget suggestions based on historical spending (Feature 1001)"""
    try:
        from dateutil.relativedelta import relativedelta

        # Get all expense categories without budgets
        categories = Category.query.filter_by(type='expense').filter(
            (Category.budget_limit.is_(None)) | (Category.budget_limit == 0)
        ).all()

        suggestions = []
        for category in categories:
            # Calculate average spending for the last 3 months
            three_months_ago = date.today() - relativedelta(months=3)
            avg_spending = db.session.query(func.avg(Transaction.amount)).filter(
                Transaction.category_id == category.id,
                Transaction.date >= three_months_ago,
                Transaction.type == 'expense'
            ).scalar()

            if avg_spending and abs(float(avg_spending)) > 0:
                # Suggest 80th percentile to allow some flexibility
                suggestion_amount = abs(float(avg_spending)) * 1.25  # Add 25% buffer
                suggestions.append({
                    'category_id': category.id,
                    'category_name': category.name,
                    'suggested_budget': round(suggestion_amount, 2),
                    'historical_average': abs(float(avg_spending)),
                    'reasoning': f'Based on 3-month average spending of ${abs(float(avg_spending)):.2f}'
                })

        return jsonify({
            'suggestions': suggestions,
            'total_suggestions': len(suggestions)
        })

    except Exception as e:
        return handle_error(f"Error generating budget suggestions: {str(e)}", 500)

@api.route('/budget/calculate-effective', methods=['GET', 'POST'])
def calculate_effective_budget():
    """Calculate effective budget amounts for all categories (Feature 1001)

    - GET: returns { calculations: [...], total_income }
    - POST: returns { effective_budgets: [...], total_categories, total_budget }
    """
    try:
        if request.method == 'POST':
            data = request.get_json(silent=True) or {}
            total_income = float(data.get('total_income', 0.0) or 0.0)

            categories = Category.query.filter_by(type='expense').all()
            items = []
            total_budget = 0.0

            for category in categories:
                effective_amount = category.calculate_effective_budget(total_income)
                total_budget += float(category.budget_limit or 0.0)
                items.append({
                    'category_id': category.id,
                    'category_name': category.name,
                    'effective_amount': effective_amount,
                    'budget_type': category.budget_type,
                    'budget_period': category.budget_period
                })

            return jsonify({
                'effective_budgets': items,
                'total_categories': len(categories),
                'total_budget': total_budget,
                'generated_at': datetime.now().isoformat()
            })

        # GET branch (default)
        total_income = float(request.args.get('total_income', 0.0) or 0.0)

        categories = Category.query.filter_by(type='expense').all()
        effective_budgets = []

        for category in categories:
            effective_budget = category.calculate_effective_budget(total_income)
            effective_budgets.append({
                'category_id': category.id,
                'category_name': category.name,
                'effective_budget': effective_budget,
                'calculation_method': f"{category.budget_type} budget for {category.budget_period} period",
                'factors': {
                    'total_income': total_income,
                    'percentage_used': float(category.budget_percentage) if category.budget_percentage else None
                }
            })

        return jsonify({
            'calculations': effective_budgets,
            'total_income': total_income,
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        return handle_error(f"Error calculating effective budgets: {str(e)}", 500)

@api.route('/budget/copy-template', methods=['POST'])
def copy_budget_template():
    """Copy budget settings from a previous period with inflation adjustment (Feature 1001)"""
    try:
        data = request.get_json()
        source_period = data.get('source_period', 'last_month')
        inflation_rate = data.get('inflation_rate', 0.0)  # Percentage

        # Get all expense categories with budgets
        categories = Category.query.filter_by(type='expense').filter(
            Category.budget_limit.isnot(None)
        ).all()

        updated_categories = []
        for category in categories:
            if category.budget_limit:
                # Apply inflation adjustment
                new_budget = float(category.budget_limit) * (1 + inflation_rate / 100.0)
                category.budget_limit = new_budget
                updated_categories.append({
                    'category_id': category.id,
                    'category_name': category.name,
                    'original_budget': float(category.budget_limit) / (1 + inflation_rate / 100.0),
                    'new_budget': new_budget,
                    'inflation_adjustment': inflation_rate
                })

        db.session.commit()

        return jsonify({
            'message': f'Budget template copied from {source_period} with {inflation_rate}% inflation adjustment',
            'updated_categories': updated_categories,
            'total_updated': len(updated_categories)
        })

    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error copying budget template: {str(e)}", 500)

@api.route('/budget/progress', methods=['GET'])
def get_budget_progress():
    """Get budget progress for all expense categories (Feature 1001)"""
    try:
        from dateutil.relativedelta import relativedelta
        from datetime import date

        # Get all expense categories
        expense_categories = Category.query.filter_by(type='expense').all()

        progress_data = []
        summary = {
            'total_budgeted': 0.0,
            'total_spent': 0.0,
            'total_remaining': 0.0,
            'overall_progress': 0.0,
            'categories_count': len(expense_categories),
            'categories_over_budget': 0,
            'categories_warning': 0,
            'categories_under_budget': 0
        }

        for category in expense_categories:
            if not category.budget_limit or category.budget_limit <= 0:
                continue

            # Calculate spending for current month
            current_date = date.today()
            start_of_month = date(current_date.year, current_date.month, 1)

            spent_query = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.category_id == category.id,
                Transaction.type == 'expense',
                Transaction.date >= start_of_month
            )
            spent = abs(float(spent_query.scalar() or 0))

            budget_limit = float(category.budget_limit)
            remaining = budget_limit - spent
            percentage = (spent / budget_limit) * 100

            # Determine status
            if percentage > 100:
                status = 'over'
                summary['categories_over_budget'] += 1
            elif percentage > 80:
                status = 'warning'
                summary['categories_warning'] += 1
            else:
                status = 'under'
                summary['categories_under_budget'] += 1

            # Calculate days remaining in month
            if current_date.month == 12:
                next_month = date(current_date.year + 1, 1, 1)
            else:
                next_month = date(current_date.year, current_date.month + 1, 1)

            days_remaining = (next_month - current_date).days

            # Calculate daily pace
            daily_pace = spent / max(1, current_date.day)

            # Calculate projected overspend if applicable
            projected_overspend = 0
            if daily_pace > 0:
                projected_daily_needed = budget_limit / 30  # Assume 30 days in month
                if daily_pace > projected_daily_needed:
                    projected_overspend = (daily_pace - projected_daily_needed) * (30 - current_date.day)

            progress_data.append({
                'category_id': category.id,
                'category_name': category.name,
                'budget_limit': budget_limit,
                'spent_amount': spent,
                'remaining_amount': remaining,
                'spent_percentage': percentage,
                'status': status,
                'days_remaining': days_remaining,
                'daily_pace': daily_pace,
                'projected_overspend': projected_overspend
            })

            # Update summary totals
            summary['total_budgeted'] += budget_limit
            summary['total_spent'] += spent
            summary['total_remaining'] += remaining

        # Calculate overall progress
        if summary['total_budgeted'] > 0:
            summary['overall_progress'] = (summary['total_spent'] / summary['total_budgeted']) * 100

        return jsonify({
            'progress': progress_data,
            'summary': summary,
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        return handle_error(f"Error fetching budget progress: {str(e)}", 500)

# ============================================================================
# ADVANCED BUDGET TRACKING ENDPOINTS (Feature 1002)
# ============================================================================

@api.route('/budget/progress/advanced', methods=['GET'])
def get_budget_progress_advanced_endpoint():
    """Get advanced budget progress with predictions and analytics (Feature 1002)"""
    try:
        # Get date range parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return handle_error("Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return handle_error("Invalid end_date format. Use YYYY-MM-DD")

        progress_data = get_budget_progress_advanced(start_date, end_date)

        # Calculate summary
        total_budgeted = sum(item['budget_limit'] for item in progress_data)
        total_spent = sum(item['spent_amount'] for item in progress_data)
        total_remaining = sum(item['remaining_amount'] for item in progress_data)

        categories_over_budget = sum(1 for item in progress_data if item['status'] == 'over')
        categories_warning = sum(1 for item in progress_data if item['status'] == 'warning')
        categories_under_budget = sum(1 for item in progress_data if item['status'] == 'under')

        average_health_score = sum(item['health_score'] for item in progress_data) / len(progress_data) if progress_data else 100

        summary = {
            'total_budgeted': total_budgeted,
            'total_spent': total_spent,
            'total_remaining': total_remaining,
            'overall_progress': (total_spent / total_budgeted) * 100 if total_budgeted > 0 else 0,
            'categories_count': len(progress_data),
            'categories_over_budget': categories_over_budget,
            'categories_warning': categories_warning,
            'categories_under_budget': categories_under_budget,
            'average_health_score': average_health_score,
            'performance_score': get_budget_performance_score()
        }

        # Generate alerts based on advanced analytics
        alerts = []
        for item in progress_data:
            if item['pace_analysis']['predicted_overspend'] > 0:
                alerts.append({
                    'type': 'warning',
                    'category': item['category_name'],
                    'message': f"Predicted overspend of ${item['pace_analysis']['predicted_overspend']:.2f} if current pace continues",
                    'severity': 'high' if item['pace_analysis']['pace_ratio'] > 2 else 'medium'
                })

            if item['health_score'] < 60:
                alerts.append({
                    'type': 'health',
                    'category': item['category_name'],
                    'message': f"Budget health score is {item['health_score']:.1f}/100 - consider adjustments",
                    'severity': 'high' if item['health_score'] < 40 else 'medium'
                })

        return jsonify({
            'progress': progress_data,
            'summary': summary,
            'alerts': alerts,
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        return handle_error(f"Error fetching advanced budget progress: {str(e)}", 500)

@api.route('/budget/trends/historical', methods=['GET'])
def get_budget_historical_trends_endpoint():
    """Get historical budget performance trends (Feature 1002)"""
    try:
        months = request.args.get('months', 6, type=int)

        if months < 1 or months > 24:
            return handle_error("Months must be between 1 and 24")

        trends = get_budget_historical_trends(months)

        return jsonify({
            'trends': trends,
            'period_months': months,
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        return handle_error(f"Error fetching budget trends: {str(e)}", 500)

@api.route('/budget/transaction-impact/<int:transaction_id>', methods=['GET'])
def get_transaction_budget_impact_endpoint(transaction_id):
    """Get budget impact analysis for a specific transaction (Feature 1002)"""
    try:
        impact_analysis = get_transaction_budget_impact(transaction_id)

        if impact_analysis is None:
            return handle_error("Transaction not found or not an expense", 404)

        return jsonify({
            'impact_analysis': impact_analysis,
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        return handle_error(f"Error analyzing transaction impact: {str(e)}", 500)

@api.route('/budget/performance-score', methods=['GET'])
def get_budget_performance_score_endpoint():
    """Get overall budget performance score (Feature 1002)"""
    try:
        score = get_budget_performance_score()

        # Get additional performance metrics
        categories = Category.query.filter_by(type='expense').filter(
            Category.budget_limit.isnot(None)
        ).all()

        performance_metrics = {
            'overall_score': score,
            'categories_tracked': len(categories),
            'score_interpretation': _interpret_performance_score(score)
        }

        return jsonify({
            'performance': performance_metrics,
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        return handle_error(f"Error calculating performance score: {str(e)}", 500)

@api.route('/budget/predictive-alerts', methods=['GET'])
def get_budget_predictive_alerts():
    """Get predictive spending alerts (Feature 1002)"""
    try:
        progress_data = get_budget_progress_advanced()

        alerts = []

        for item in progress_data:
            # Daily pace alerts
            if item['pace_analysis']['pace_ratio'] > 1.5:
                days_to_overspend = None
                if item['pace_analysis']['pace_ratio'] > 1:
                    remaining_budget = item['remaining_amount']
                    daily_excess = item['pace_analysis']['daily_pace'] - item['pace_analysis']['expected_daily']
                    if daily_excess > 0:
                        days_to_overspend = remaining_budget / daily_excess

                alerts.append({
                    'type': 'pace',
                    'category_id': item['category_id'],
                    'category_name': item['category_name'],
                    'severity': 'high' if item['pace_analysis']['pace_ratio'] > 2 else 'medium',
                    'message': f"Spending {item['pace_analysis']['pace_ratio']:.1f}x faster than planned",
                    'current_pace': item['pace_analysis']['daily_pace'],
                    'expected_pace': item['pace_analysis']['expected_daily'],
                    'days_to_overspend': days_to_overspend,
                    'predicted_overspend': item['pace_analysis']['predicted_overspend']
                })

            # Variance alerts
            if abs(item['variance_analysis']['variance_percentage']) > 20:
                alerts.append({
                    'type': 'variance',
                    'category_id': item['category_id'],
                    'category_name': item['category_name'],
                    'severity': 'medium',
                    'message': f"{'Over' if item['variance_analysis']['variance_percentage'] > 0 else 'Under'} spending by {abs(item['variance_analysis']['variance_percentage']):.1f}% vs expected",
                    'expected_spent': item['variance_analysis']['expected_spent'],
                    'actual_spent': item['spent_amount'],
                    'variance_amount': item['variance_analysis']['variance_amount']
                })

            # Health score alerts
            if item['health_score'] < 70:
                alerts.append({
                    'type': 'health',
                    'category_id': item['category_id'],
                    'category_name': item['category_name'],
                    'severity': 'high' if item['health_score'] < 50 else 'medium',
                    'message': f"Budget health score: {item['health_score']:.1f}/100",
                    'health_score': item['health_score'],
                    'recommendation': _get_health_recommendation(item['health_score'])
                })

        # Sort alerts by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 2))

        return jsonify({
            'alerts': alerts,
            'total_alerts': len(alerts),
            'high_priority': len([a for a in alerts if a['severity'] == 'high']),
            'medium_priority': len([a for a in alerts if a['severity'] == 'medium']),
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        return handle_error(f"Error generating predictive alerts: {str(e)}", 500)

def _interpret_performance_score(score):
    """Interpret the performance score with human-readable description"""
    if score >= 90:
        return "Excellent - All budgets are well managed"
    elif score >= 80:
        return "Good - Most budgets are on track"
    elif score >= 70:
        return "Fair - Some budget adjustments recommended"
    elif score >= 60:
        return "Needs Attention - Multiple budgets require monitoring"
    else:
        return "Critical - Immediate budget review needed"

def _get_health_recommendation(health_score):
    """Get health-based recommendations"""
    if health_score >= 80:
        return "Keep up the great work!"
    elif health_score >= 60:
        return "Monitor spending closely and consider minor adjustments"
    elif health_score >= 40:
        return "Review spending patterns and adjust budget limits"
    else:
        return "Significant budget adjustments needed to get back on track"

# ============================================================================
# BUDGET METHODOLOGY ROUTES (Feature 1005)
# ============================================================================

@api.route('/budget/methodologies', methods=['GET'])
def get_budget_methodologies():
    """Get all available budget methodologies"""
    try:
        methodologies = BudgetMethodology.query.all()
        return jsonify([methodology.to_dict() for methodology in methodologies])
    except Exception as e:
        return handle_error(f"Error fetching budget methodologies: {str(e)}", 500)

@api.route('/budget/methodologies', methods=['POST'])
def create_budget_methodology():
    """Create a new budget methodology"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'name' not in data or 'methodology_type' not in data:
            return handle_error("Name and methodology_type are required fields")
        
        # Validate methodology type
        valid_types = ['zero_based', 'percentage_based', 'envelope']
        if data['methodology_type'] not in valid_types:
            return handle_error(f"methodology_type must be one of: {', '.join(valid_types)}")
        
        # Check if methodology already exists
        existing = BudgetMethodology.query.filter_by(name=data['name']).first()
        if existing:
            return handle_error("Methodology with this name already exists")
        
        # Validate configuration if provided
        configuration = data.get('configuration', {})
        if configuration and data['methodology_type'] == 'percentage_based':
            # Validate percentage configuration
            needs = configuration.get('needs_percentage', 50)
            wants = configuration.get('wants_percentage', 30)
            savings = configuration.get('savings_percentage', 20)
            
            if needs + wants + savings != 100:
                return handle_error("Percentage-based configuration must sum to 100%")
        
        # Create new methodology
        methodology = BudgetMethodology(
            name=data['name'],
            description=data.get('description', ''),
            methodology_type=data['methodology_type'],
            is_active=data.get('is_active', False),
            is_default=data.get('is_default', False)
        )
        
        if configuration:
            methodology.set_configuration(configuration)
        
        # If setting as active, deactivate others first
        if data.get('is_active', False):
            BudgetMethodology.query.update({'is_active': False})
        
        db.session.add(methodology)
        db.session.commit()
        
        return jsonify(methodology.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error creating budget methodology: {str(e)}", 500)

@api.route('/budget/methodologies/<int:methodology_id>', methods=['PUT'])
def update_budget_methodology(methodology_id):
    """Update an existing budget methodology"""
    try:
        methodology = db.session.get(BudgetMethodology, methodology_id)
        if methodology is None:
            return handle_error("Budget methodology not found", 404)
        
        data = request.get_json()
        
        if 'name' in data:
            # Check if new name conflicts with existing methodology
            existing = BudgetMethodology.query.filter_by(name=data['name']).first()
            if existing and existing.id != methodology_id:
                return handle_error("Methodology with this name already exists")
            methodology.name = data['name']
        
        if 'description' in data:
            methodology.description = data['description']
        
        if 'methodology_type' in data:
            valid_types = ['zero_based', 'percentage_based', 'envelope']
            if data['methodology_type'] not in valid_types:
                return handle_error(f"methodology_type must be one of: {', '.join(valid_types)}")
            methodology.methodology_type = data['methodology_type']
        
        if 'configuration' in data:
            # Validate configuration
            configuration = data['configuration']
            if configuration and methodology.methodology_type == 'percentage_based':
                needs = configuration.get('needs_percentage', 50)
                wants = configuration.get('wants_percentage', 30)
                savings = configuration.get('savings_percentage', 20)
                
                if needs + wants + savings != 100:
                    return handle_error("Percentage-based configuration must sum to 100%")
            
            methodology.set_configuration(configuration)
        
        if 'is_active' in data:
            if data['is_active']:
                # Deactivate all other methodologies
                BudgetMethodology.query.update({'is_active': False})
            methodology.is_active = data['is_active']
        
        if 'is_default' in data:
            methodology.is_default = data['is_default']
        
        db.session.commit()
        return jsonify(methodology.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error updating budget methodology: {str(e)}", 500)

@api.route('/budget/methodologies/<int:methodology_id>', methods=['DELETE'])
def delete_budget_methodology(methodology_id):
    """Delete a budget methodology"""
    try:
        methodology = db.session.get(BudgetMethodology, methodology_id)
        if methodology is None:
            return handle_error("Budget methodology not found", 404)
        
        # Prevent deletion of active methodology
        if methodology.is_active:
            return handle_error("Cannot delete active methodology. Please activate another methodology first.", 400)
        
        db.session.delete(methodology)
        db.session.commit()
        
        return jsonify({'message': 'Budget methodology deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error deleting budget methodology: {str(e)}", 500)

@api.route('/budget/methodologies/active', methods=['GET'])
def get_active_methodology_endpoint():
    """Get the currently active budget methodology"""
    try:
        methodology = get_active_methodology()
        if methodology:
            return jsonify(methodology.to_dict())
        else:
            return jsonify({'message': 'No active methodology set'}), 404
    except Exception as e:
        return handle_error(f"Error fetching active methodology: {str(e)}", 500)

@api.route('/budget/methodologies/<int:methodology_id>/activate', methods=['POST'])
def activate_methodology(methodology_id):
    """Activate a specific budget methodology"""
    try:
        methodology = set_active_methodology(methodology_id)
        if methodology:
            return jsonify({
                'message': f'Methodology "{methodology.name}" activated successfully',
                'methodology': methodology.to_dict()
            })
        else:
            return handle_error("Methodology not found", 404)
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error activating methodology: {str(e)}", 500)

@api.route('/budget/methodologies/<int:methodology_id>/calculate', methods=['GET', 'POST'])
def calculate_methodology_budget_endpoint(methodology_id):
    """Calculate budget using specified methodology"""
    try:
        # Get total income from request or calculate from current month
        if request.method == 'POST':
            data = request.get_json() or {}
            total_income = data.get('total_income')
        else:
            total_income = request.args.get('total_income', type=float)
        
        calculation_result = calculate_methodology_budget(methodology_id, total_income)
        
        return jsonify({
            'calculation_result': calculation_result,
            'generated_at': datetime.now().isoformat()
        })
        
    except ValueError as e:
        return handle_error(str(e), 404)
    except Exception as e:
        return handle_error(f"Error calculating methodology budget: {str(e)}", 500)

@api.route('/budget/methodologies/<int:methodology_id>/apply', methods=['POST'])
def apply_methodology_endpoint(methodology_id):
    """Apply methodology calculations to category budgets"""
    try:
        data = request.get_json() or {}
        total_income = data.get('total_income')
        auto_update = data.get('auto_update', False)
        
        calculation_result = apply_methodology_to_categories(
            methodology_id, total_income, auto_update
        )
        
        return jsonify({
            'message': 'Methodology applied successfully' if auto_update else 'Methodology calculated successfully',
            'calculation_result': calculation_result,
            'auto_updated': auto_update,
            'generated_at': datetime.now().isoformat()
        })
        
    except ValueError as e:
        return handle_error(str(e), 404)
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error applying methodology: {str(e)}", 500)

@api.route('/budget/methodologies/<int:methodology_id>/validate', methods=['GET'])
def validate_methodology_configuration(methodology_id):
    """Validate methodology configuration"""
    try:
        methodology = db.session.get(BudgetMethodology, methodology_id)
        if not methodology:
            return handle_error("Methodology not found", 404)
        
        # Create engine to validate configuration
        engine = BudgetMethodologyFactory.create_engine(methodology)
        is_valid, error_message = engine.validate_configuration()
        
        return jsonify({
            'methodology_id': methodology_id,
            'methodology_name': methodology.name,
            'is_valid': is_valid,
            'error_message': error_message,
            'configuration': methodology.get_configuration()
        })
        
    except ValueError as e:
        return handle_error(str(e), 404)
    except Exception as e:
        return handle_error(f"Error validating methodology: {str(e)}", 500)

@api.route('/budget/methodologies/compare', methods=['POST'])
def compare_methodologies():
    """Compare multiple budget methodologies for the same income"""
    try:
        data = request.get_json()
        methodology_ids = data.get('methodology_ids', [])
        total_income = data.get('total_income')
        
        if not methodology_ids:
            return handle_error("methodology_ids are required")
        
        if len(methodology_ids) > 5:
            return handle_error("Cannot compare more than 5 methodologies at once")
        
        comparisons = []
        
        for methodology_id in methodology_ids:
            try:
                calculation_result = calculate_methodology_budget(methodology_id, total_income)
                methodology = db.session.get(BudgetMethodology, methodology_id)
                
                comparisons.append({
                    'methodology_id': methodology_id,
                    'methodology_name': methodology.name,
                    'methodology_type': methodology.methodology_type,
                    'calculation_result': calculation_result
                })
                
            except ValueError:
                # Skip invalid methodologies
                continue
        
        return jsonify({
            'comparisons': comparisons,
            'total_income': total_income,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return handle_error(f"Error comparing methodologies: {str(e)}", 500)

@api.route('/budget/methodologies/recommendations', methods=['GET'])
def get_methodology_recommendations():
    """Get personalized methodology recommendations based on user data"""
    try:
        # Get user's current spending patterns
        current_date = date.today()
        month_start = date(current_date.year, current_date.month, 1)
        
        total_income = get_total_income(month_start, current_date)
        total_expenses = get_total_expenses(month_start, current_date)
        
        # Get categories with current spending
        categories = Category.query.filter_by(type='expense').all()
        spending_pattern = {}
        
        for category in categories:
            spent = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.category_id == category.id,
                Transaction.type == 'expense',
                Transaction.date >= month_start
            ).scalar()
            spending_pattern[category.id] = abs(float(spent or 0))
        
        # Calculate savings rate
        savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
        
        recommendations = []
        
        # Recommend Zero-Based if low savings rate
        if savings_rate < 10:
            recommendations.append({
                'methodology_type': 'zero_based',
                'reason': 'Low savings rate detected. Zero-based budgeting helps ensure every dollar has a purpose.',
                'confidence': 85,
                'best_for': 'Users who want strict control over spending and to maximize savings'
            })
        
        # Recommend 50/30/20 if balanced spending
        if 10 <= savings_rate <= 25:
            recommendations.append({
                'methodology_type': 'percentage_based',
                'reason': 'Balanced financial profile. The 50/30/20 rule provides good structure while maintaining flexibility.',
                'confidence': 80,
                'best_for': 'Users who want simple guidelines without micromanaging every expense'
            })
        
        # Recommend Envelope if variable income or overspending issues
        has_budget_issues = any(
            category.budget_limit and spending_pattern.get(category.id, 0) > float(category.budget_limit)
            for category in categories if category.budget_limit
        )
        
        if has_budget_issues:
            recommendations.append({
                'methodology_type': 'envelope',
                'reason': 'Detected overspending in some categories. Envelope budgeting provides strict spending limits.',
                'confidence': 75,
                'best_for': 'Users who struggle with overspending and need clear spending boundaries'
            })
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return jsonify({
            'recommendations': recommendations,
            'user_profile': {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'savings_rate': savings_rate,
                'categories_count': len(categories),
                'overspending_categories': sum(1 for cat in categories if cat.budget_limit and spending_pattern.get(cat.id, 0) > float(cat.budget_limit))
            },
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return handle_error(f"Error generating methodology recommendations: {str(e)}", 500)