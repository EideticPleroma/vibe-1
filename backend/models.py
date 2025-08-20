"""
Database models for Personal Finance App
Defines SQLAlchemy models for categories, transactions, and investments
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func
import json

from datetime import timezone

db = SQLAlchemy()

class Category(db.Model):
    """Enhanced budget category model with flexible budgeting support"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    color = db.Column(db.String(7), nullable=False, default='#007bff')  # Hex color

    # Enhanced Budget Fields (Feature 1001)
    budget_limit = db.Column(db.Numeric(10, 2), nullable=True, default=0.0)  # Base budget amount
    budget_period = db.Column(db.String(20), nullable=False, default='monthly')  # daily, weekly, monthly, yearly
    budget_type = db.Column(db.String(20), nullable=False, default='fixed')  # fixed, percentage, rolling_average
    budget_priority = db.Column(db.String(20), nullable=False, default='essential')  # critical, essential, important, discretionary

    # Budget Type Specific Fields
    budget_percentage = db.Column(db.Numeric(5, 2), nullable=True)  # For percentage-based budgets
    budget_rolling_months = db.Column(db.Integer, nullable=False, default=3)  # For rolling average calculations

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy=True)

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'color': self.color,
            'budget_limit': float(self.budget_limit) if self.budget_limit else None,
            'budget_period': self.budget_period,
            'budget_type': self.budget_type,
            'budget_priority': self.budget_priority,
            'budget_percentage': float(self.budget_percentage) if self.budget_percentage else None,
            'budget_rolling_months': self.budget_rolling_months,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def calculate_effective_budget(self, total_income=None):
        """Calculate the effective budget amount based on budget type"""
        if not self.budget_limit:
            return 0.0

        if self.budget_type == 'fixed':
            return float(self.budget_limit)
        elif self.budget_type == 'percentage' and total_income and self.budget_percentage:
            return float(total_income) * (float(self.budget_percentage) / 100.0)
        elif self.budget_type == 'rolling_average':
            # This would require historical data analysis - placeholder for now
            return float(self.budget_limit)
        else:
            return float(self.budget_limit)

    def get_budget_period_days(self):
        """Get the number of days for the budget period"""
        period_days = {
            'daily': 1,
            'weekly': 7,
            'monthly': 30,  # Approximation
            'yearly': 365
        }
        return period_days.get(self.budget_period, 30)

    def get_budget_health_score(self, spent_amount, period_days_elapsed):
        """Calculate budget health score (0-100)"""
        if not self.budget_limit or self.budget_limit <= 0:
            return 100  # No budget set = perfect health

        budget_limit = float(self.budget_limit)
        spent = float(spent_amount)

        # Calculate expected spending based on time elapsed
        expected_spent = (budget_limit / self.get_budget_period_days()) * period_days_elapsed

        if spent <= expected_spent:
            # Under or on pace - score based on how much buffer remains
            remaining_buffer = budget_limit - spent
            return min(100, 80 + (remaining_buffer / budget_limit) * 20)
        else:
            # Over pace - score based on how much over
            overspend_ratio = (spent - expected_spent) / expected_spent
            return max(0, 80 - (overspend_ratio * 50))

    def __repr__(self):
        return f'<Category {self.name} ({self.type}) - {self.budget_type} {self.budget_period} budget>'

class Transaction(db.Model):
    """Financial transaction model"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    @hybrid_property
    def is_income(self):
        """Check if transaction is income"""
        return self.type == 'income'
    
    @hybrid_property
    def is_expense(self):
        """Check if transaction is expense"""
        return self.type == 'expense'
    
    @hybrid_property
    def absolute_amount(self):
        """Get absolute value of amount"""
        return abs(float(self.amount))
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'amount': float(self.amount),
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'category_color': self.category.color if self.category else None,
            'description': self.description,
            'type': self.type,
            'is_income': self.is_income,
            'is_expense': self.is_expense,
            'absolute_amount': self.absolute_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Transaction {self.description} ({self.amount}) on {self.date}>'

class Investment(db.Model):
    """Investment holding model"""
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(100), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)  # 'stock', 'crypto', 'bond', etc.
    quantity = db.Column(db.Numeric(15, 6), nullable=False)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    current_price = db.Column(db.Numeric(10, 2), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    @hybrid_property
    def total_invested(self):
        """Calculate total amount invested"""
        return float(self.quantity) * float(self.purchase_price)
    
    @hybrid_property
    def current_value(self):
        """Calculate current total value"""
        return float(self.quantity) * float(self.current_price)
    
    @hybrid_property
    def total_gain_loss(self):
        """Calculate total gain/loss"""
        return self.current_value - self.total_invested
    
    @hybrid_property
    def gain_loss_percentage(self):
        """Calculate gain/loss percentage"""
        if self.total_invested == 0:
            return 0
        return (self.total_gain_loss / self.total_invested) * 100
    
    @hybrid_property
    def is_profitable(self):
        """Check if investment is profitable"""
        return self.total_gain_loss > 0
    
    def update_current_price(self, new_price):
        """Update current price and recalculate values"""
        self.current_price = new_price
        self.updated_at = datetime.now(timezone.utc)
        return self
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'asset_name': self.asset_name,
            'asset_type': self.asset_type,
            'quantity': float(self.quantity),
            'purchase_price': float(self.purchase_price),
            'current_price': float(self.current_price),
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'total_invested': self.total_invested,
            'current_value': self.current_value,
            'total_gain_loss': self.total_gain_loss,
            'gain_loss_percentage': self.gain_loss_percentage,
            'is_profitable': self.is_profitable,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Investment {self.asset_name} ({self.quantity} @ ${self.current_price})>'

# Utility functions for common operations
def get_total_income(start_date=None, end_date=None):
    """Get total income for a date range"""
    query = Transaction.query.filter_by(type='income')
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    result = query.with_entities(db.func.sum(Transaction.amount)).scalar()
    return float(result) if result else 0.0

def get_total_expenses(start_date=None, end_date=None):
    """Get total expenses for a date range"""
    query = Transaction.query.filter_by(type='expense')
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    result = query.with_entities(db.func.sum(Transaction.amount)).scalar()
    return abs(float(result)) if result else 0.0

def get_net_income(start_date=None, end_date=None):
    """Get net income (income - expenses) for a date range"""
    income = get_total_income(start_date, end_date)
    expenses = get_total_expenses(start_date, end_date)
    return income - expenses

def get_total_investment_value():
    """Get total current value of all investments"""
    result = db.session.query(db.func.sum(Investment.quantity * Investment.current_price)).scalar()
    return float(result or 0)

def get_total_investment_gain_loss():
    """Get total gain/loss across all investments"""
    result = db.session.query(db.func.sum(
        (Investment.quantity * Investment.current_price) - (Investment.quantity * Investment.purchase_price)
    )).scalar()
    return float(result or 0)

def update_investment_prices():
    """
    Placeholder function for updating investment prices
    CUSTOMIZATION POINT: Implement your own price update logic here

    This could include:
    - API calls to financial data providers
    - Web scraping from financial websites
    - Integration with trading platforms
    - Real-time price feeds
    """
    print("Investment price update function called - customize this for your needs!")

    # Example implementation structure:
    # for investment in Investment.query.all():
    #     if investment.asset_type == 'stock':
    #         new_price = get_stock_price(investment.asset_name)
    #     elif investment.asset_type == 'crypto':
    #         new_price = get_crypto_price(investment.asset_name)
    #     else:
    #         new_price = get_other_asset_price(investment.asset_name)
    #
    #     investment.update_current_price(new_price)
    #
    # db.session.commit()

    return True

# Advanced Budget Tracking Functions (Feature 1002)
def get_budget_progress_advanced(start_date=None, end_date=None, include_predictions=True):
    """Get advanced budget progress with predictions and analytics"""
    from datetime import datetime, date, timedelta
    from sqlalchemy import func, case

    # Get all expense categories with budgets
    expense_categories = Category.query.filter_by(type='expense').filter(
        Category.budget_limit.isnot(None)
    ).all()

    progress_data = []
    current_date = date.today()

    for category in expense_categories:
        # Calculate spending for the period
        spending_query = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.category_id == category.id,
            Transaction.type == 'expense'
        )

        if start_date:
            spending_query = spending_query.filter(Transaction.date >= start_date)
        if end_date:
            spending_query = spending_query.filter(Transaction.date <= end_date)

        spent_amount = abs(float(spending_query.scalar() or 0))
        budget_limit = float(category.budget_limit)

        # Calculate period information
        if start_date and end_date:
            total_days = (end_date - start_date).days
            days_elapsed = (min(current_date, end_date) - start_date).days
        else:
            # Default to current month
            month_start = date(current_date.year, current_date.month, 1)
            if current_date.month == 12:
                month_end = date(current_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(current_date.year, current_date.month + 1, 1) - timedelta(days=1)

            total_days = (month_end - month_start).days
            days_elapsed = (current_date - month_start).days
            start_date = month_start
            end_date = month_end

        # Calculate progress metrics
        spent_percentage = (spent_amount / budget_limit) * 100 if budget_limit > 0 else 0
        remaining_amount = budget_limit - spent_amount
        daily_pace = spent_amount / max(1, days_elapsed)
        expected_daily = budget_limit / max(1, total_days)
        pace_ratio = daily_pace / expected_daily if expected_daily > 0 else 1

        # Determine status
        if spent_percentage > 100:
            status = 'over'
        elif spent_percentage > 80:
            status = 'warning'
        else:
            status = 'under'

        # Calculate health score
        health_score = category.get_budget_health_score(spent_amount, days_elapsed)

        # Predictive analytics
        remaining_days = max(0, total_days - days_elapsed)
        predicted_overspend = 0
        if daily_pace > expected_daily:
            predicted_overspend = (daily_pace - expected_daily) * remaining_days

        # Calculate variance from expected
        expected_spent = expected_daily * days_elapsed
        variance_amount = spent_amount - expected_spent
        variance_percentage = (variance_amount / expected_spent) * 100 if expected_spent > 0 else 0

        progress_data.append({
            'category_id': category.id,
            'category_name': category.name,
            'budget_limit': budget_limit,
            'spent_amount': spent_amount,
            'remaining_amount': remaining_amount,
            'spent_percentage': spent_percentage,
            'status': status,
            'health_score': health_score,
            'period_info': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_days': total_days,
                'days_elapsed': days_elapsed,
                'days_remaining': remaining_days
            },
            'pace_analysis': {
                'daily_pace': daily_pace,
                'expected_daily': expected_daily,
                'pace_ratio': pace_ratio,
                'predicted_overspend': predicted_overspend
            },
            'variance_analysis': {
                'expected_spent': expected_spent,
                'variance_amount': variance_amount,
                'variance_percentage': variance_percentage
            }
        })

    return progress_data

def get_budget_historical_trends(months=6):
    """Get historical budget performance trends"""
    from datetime import datetime, date, timedelta
    from dateutil.relativedelta import relativedelta
    import calendar

    # Get all expense categories with budgets
    categories = Category.query.filter_by(type='expense').filter(
        Category.budget_limit.isnot(None)
    ).all()

    end_date = date.today()
    start_date = end_date - relativedelta(months=months)

    trends = []

    # Generate monthly data points
    current_date = start_date
    while current_date <= end_date:
        month_start = date(current_date.year, current_date.month, 1)
        month_end = date(current_date.year, current_date.month,
                        calendar.monthrange(current_date.year, current_date.month)[1])

        monthly_data = {
            'period': f"{current_date.strftime('%Y-%m')}",
            'period_start': month_start.isoformat(),
            'period_end': month_end.isoformat(),
            'categories': []
        }

        total_budgeted = 0
        total_spent = 0

        for category in categories:
            # Get spending for this month
            spent = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.category_id == category.id,
                Transaction.type == 'expense',
                Transaction.date >= month_start,
                Transaction.date <= month_end
            ).scalar()

            spent = abs(float(spent or 0))
            budget_limit = float(category.budget_limit or 0)

            monthly_data['categories'].append({
                'category_id': category.id,
                'category_name': category.name,
                'budget_limit': budget_limit,
                'spent_amount': spent,
                'spent_percentage': (spent / budget_limit) * 100 if budget_limit > 0 else 0,
                'health_score': category.get_budget_health_score(spent, (month_end - month_start).days)
            })

            total_budgeted += budget_limit
            total_spent += spent

        monthly_data['total_budgeted'] = total_budgeted
        monthly_data['total_spent'] = total_spent
        monthly_data['total_remaining'] = total_budgeted - total_spent
        monthly_data['overall_progress'] = (total_spent / total_budgeted) * 100 if total_budgeted > 0 else 0

        trends.append(monthly_data)
        current_date = current_date + relativedelta(months=1)

    return trends

def get_transaction_budget_impact(transaction_id):
    """Get detailed budget impact analysis for a specific transaction"""
    transaction = db.session.get(Transaction, transaction_id)
    if not transaction or transaction.type != 'expense':
        return None

    category = transaction.category
    if not category or not category.budget_limit:
        return {
            'transaction_id': transaction_id,
            'budget_impact': 'No budget configured for this category',
            'severity': 'none'
        }

    # Get current month spending
    current_date = date.today()
    month_start = date(current_date.year, current_date.month, 1)

    current_month_spending = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.category_id == category.id,
        Transaction.type == 'expense',
        Transaction.date >= month_start
    ).scalar()

    current_month_spending = abs(float(current_month_spending or 0))
    budget_limit = float(category.budget_limit)

    # Calculate impact
    transaction_amount = abs(float(transaction.amount))
    spending_before = current_month_spending - transaction_amount
    spending_after = current_month_spending

    percentage_before = (spending_before / budget_limit) * 100
    percentage_after = (spending_after / budget_limit) * 100

    # Determine impact severity
    if percentage_after > 100:
        severity = 'critical'
        impact_message = f"Pushes category over budget limit"
    elif percentage_after > 80:
        severity = 'warning'
        impact_message = f"Pushes category into warning zone"
    else:
        severity = 'low'
        impact_message = f"Minimal impact on budget"

    return {
        'transaction_id': transaction_id,
        'transaction_amount': abs(transaction.amount),
        'category_name': category.name,
        'budget_limit': budget_limit,
        'spending_before': spending_before,
        'spending_after': spending_after,
        'percentage_before': percentage_before,
        'percentage_after': percentage_after,
        'percentage_change': percentage_after - percentage_before,
        'severity': severity,
        'impact_message': impact_message,
        'recommendations': _get_budget_recommendations(severity, category)
    }

def _get_budget_recommendations(severity, category):
    """Generate budget recommendations based on impact severity"""
    recommendations = []

    if severity == 'critical':
        recommendations.extend([
            f"Consider reducing spending in {category.name}",
            "Review and adjust budget limit if necessary",
            "Look for cost-saving alternatives"
        ])
    elif severity == 'warning':
        recommendations.extend([
            f"Monitor {category.name} spending closely",
            "Consider reallocating funds from other categories",
            "Plan for reduced spending in remaining days"
        ])
    else:
        recommendations.extend([
            "Budget impact is minimal",
            "Continue current spending patterns"
        ])

    return recommendations

def get_budget_performance_score():
    """Calculate overall budget performance score"""
    from datetime import date

    # Get all expense categories with budgets
    categories = Category.query.filter_by(type='expense').filter(
        Category.budget_limit.isnot(None)
    ).all()

    if not categories:
        return 100  # Perfect score if no budgets set

    total_score = 0
    current_date = date.today()
    month_start = date(current_date.year, current_date.month, 1)

    for category in categories:
        # Get current month spending
        spent = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.category_id == category.id,
            Transaction.type == 'expense',
            Transaction.date >= month_start
        ).scalar()

        spent = abs(float(spent or 0))
        days_elapsed = (current_date - month_start).days

        # Calculate category score
        category_score = category.get_budget_health_score(spent, days_elapsed)
        total_score += category_score

    # Return average score
    return total_score / len(categories)
