"""
API routes for Personal Finance App
Provides RESTful endpoints for categories, transactions, and investments
"""

from flask import Blueprint, request, jsonify
from models import (
    db, Category, Transaction, Investment,
    get_total_income, get_total_expenses, get_net_income,
    get_total_investment_value, get_total_investment_gain_loss
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
        
        if 'budget_limit' in data:
            if data['type'] != 'expense':
                return handle_error("Budget limit can only be set for expense categories")
            try:
                budget = float(data['budget_limit'])
                if budget < 0:
                    return handle_error("Budget limit must be non-negative")
            except ValueError:
                return handle_error("Invalid budget limit value")
        
        # Create new category
        category = Category(
            name=data['name'],
            type=data['type'],
            color=data.get('color', '#007bff'),
            budget_limit=float(data.get('budget_limit', 0.0)) if data.get('budget_limit') else None
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
        category = Category.query.get_or_404(category_id)
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
        
        if 'color' in data:
            category.color = data['color']
        
        if 'budget_limit' in data:
            if category.type != 'expense':
                return handle_error("Budget limit can only be set for expense categories")
            try:
                budget = float(data['budget_limit'])
                if budget < 0:
                    return handle_error("Budget limit must be non-negative")
                category.budget_limit = budget
            except ValueError:
                return handle_error("Invalid budget limit value")
        
        db.session.commit()
        return jsonify(category.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return handle_error(f"Error updating category: {str(e)}", 500)

@api.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a budget category"""
    try:
        category = Category.query.get_or_404(category_id)
        
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
        category = Category.query.get(data['category_id'])
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
        transaction = Transaction.query.get_or_404(transaction_id)
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
            category = Category.query.get(data['category_id'])
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
        transaction = Transaction.query.get_or_404(transaction_id)
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
        investment = Investment.query.get_or_404(investment_id)
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
        investment = Investment.query.get_or_404(investment_id)
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
            spent = abs(spent_query.scalar() or 0)
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
