import pytest
from app import create_app
from models import db, Category, Transaction, Investment
from datetime import date, timedelta, datetime

@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory SQLite for testing
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable for testing

    with app.app_context():
        db.create_all() # Create tables once per session
    yield app
    with app.app_context():
        db.drop_all() # Drop tables once after the session

@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        with app.app_context():
            # Clean up data in all tables before each test function
            for table in reversed(db.metadata.sorted_tables):
                db.session.execute(table.delete())
            db.session.commit()
        yield client

@pytest.fixture(scope='function')
def populated_db(client):
    with client.application.app_context():
        # Create categories
        cat_food = Category(name='Food', type='expense', color='#FF0000')
        cat_salary = Category(name='Salary', type='income', color='#00FF00')
        cat_rent = Category(name='Rent', type='expense', color='#0000FF')
        db.session.add_all([cat_food, cat_salary, cat_rent])
        db.session.commit()

        # Create transactions
        # Ensure all arguments are passed as keyword arguments
        t1 = Transaction(date=date.today(), amount=-50.00, category_id=cat_food.id, description='Groceries', type='expense')
        t2 = Transaction(date=date.today(), amount=2000.00, category_id=cat_salary.id, description='Monthly Salary', type='income')
        t3 = Transaction(date=date.today() - timedelta(days=30), amount=-1000.00, category_id=cat_rent.id, description='Apartment Rent', type='expense')
        db.session.add_all([t1, t2, t3])
        db.session.commit()

        # Create investments
        inv1 = Investment(asset_name='AAPL', asset_type='stock', quantity=10.0, purchase_price=150.0, current_price=160.0, purchase_date=date(2023, 1, 1))
        inv2 = Investment(asset_name='ETH', asset_type='crypto', quantity=0.5, purchase_price=2000.0, current_price=2200.0, purchase_date=date(2023, 6, 1))
        db.session.add_all([inv1, inv2])
        db.session.commit()
    return client

# ============================================================================
# CATEGORY TESTS
# ============================================================================

def test_get_categories(populated_db):
    response = populated_db.get('/api/categories')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3
    assert data[0]['name'] == 'Food'

def test_create_category(client):
    new_category_data = {
        'name': 'Utilities',
        'type': 'expense',
        'color': '#CCCCCC'
    }
    response = client.post('/api/categories', json=new_category_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Utilities'

def test_create_category_missing_field(client):
    response = client.post('/api/categories', json={'name': 'Invalid'})
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_update_category(populated_db):
    response = populated_db.put('/api/categories/1', json={'name': 'Groceries Updated', 'color': '#FF3333'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Groceries Updated'
    assert data['color'] == '#FF3333'

def test_delete_category(client):
    with client.application.app_context():
        # Create a category that will have no transactions
        cat_no_tx = Category(name='No Transactions', type='expense', color='#ABCDEF')
        db.session.add(cat_no_tx)
        db.session.commit()
        category_id_to_delete = cat_no_tx.id

    response = client.delete(f'/api/categories/{category_id_to_delete}')
    assert response.status_code == 200
    assert 'message' in response.get_json()

    # Verify it's deleted
    response = client.get('/api/categories')
    data = response.get_json()
    # Assuming populated_db might run first, initial count is 3. After deleting 1, should be 2 + any created by other tests
    # A more robust check might involve querying for the specific deleted category by ID
    # Or, in populated_db, ensure the default categories are always the same IDs and use those for testing.
    # For now, let's just check that it's no longer present.
    category_names = [c['name'] for c in data]
    assert 'No Transactions' not in category_names

def test_delete_category_with_transactions(populated_db):
    # Try to delete 'Food' category which has transactions
    response = populated_db.delete('/api/categories/1')
    assert response.status_code == 400 # Expect 400 as per route handler
    assert 'error' in response.get_json()

def test_create_category_with_budget(populated_db):
    data = {'name': 'Test Expense', 'type': 'expense', 'budget_limit': 100.0}
    response = populated_db.post('/api/categories', json=data)
    assert response.status_code == 201
    assert response.get_json()['budget_limit'] == 100.0

def test_update_category_budget(populated_db):
    response = populated_db.put('/api/categories/1', json={'budget_limit': 200.0})
    assert response.status_code == 200
    assert response.get_json()['budget_limit'] == 200.0

def test_budget_only_for_expense(populated_db):
    response = populated_db.put('/api/categories/2', json={'budget_limit': 100.0})  # Assuming ID 2 is income
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "Budget settings can only be configured for expense categories"

def test_create_budget_only_for_expense(client):
    data = {'name': 'Test Income', 'type': 'income', 'budget_limit': 100.0}
    response = client.post('/api/categories', json=data)
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "Budget settings can only be configured for expense categories"

# ============================================================================
# TRANSACTION TESTS
# ============================================================================

def test_get_transactions(populated_db):
    response = populated_db.get('/api/transactions')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['transactions']) == 3
    assert data['pagination']['total'] == 3

def test_create_transaction(populated_db):
    new_transaction_data = {
        'date': '2023-08-15',
        'amount': 75.00,
        'category_id': 1, # Food
        'description': 'Dinner with friends',
        'type': 'expense'
    }
    response = populated_db.post('/api/transactions', json=new_transaction_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['description'] == 'Dinner with friends'
    assert float(data['amount']) == -75.00 # Expense should be negative

def test_update_transaction(populated_db):
    # Update existing transaction (t1 - Groceries)
    response = populated_db.put('/api/transactions/1', json={'amount': 60.00, 'description': 'Groceries Updated'})
    assert response.status_code == 200
    data = response.get_json()
    assert float(data['amount']) == -60.00
    assert data['description'] == 'Groceries Updated'

def test_delete_transaction(populated_db):
    response = populated_db.delete('/api/transactions/1')
    assert response.status_code == 200
    assert 'message' in response.get_json()

    response = populated_db.get('/api/transactions')
    data = response.get_json()
    assert len(data['transactions']) == 2

# ============================================================================
# INVESTMENT TESTS
# ============================================================================

def test_get_investments(populated_db):
    response = populated_db.get('/api/investments')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['asset_name'] == 'AAPL'

def test_create_investment(client):
    new_investment_data = {
        'asset_name': 'GOOG',
        'asset_type': 'stock',
        'quantity': 5.0,
        'purchase_price': 100.0,
        'current_price': 105.0,
        'purchase_date': '2024-01-01'
    }
    response = client.post('/api/investments', json=new_investment_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['asset_name'] == 'GOOG'
    assert float(data['quantity']) == 5.0

def test_update_investment(populated_db):
    response = populated_db.put('/api/investments/1', json={'current_price': 170.0})
    assert response.status_code == 200
    data = response.get_json()
    assert float(data['current_price']) == 170.0
    assert float(data['total_gain_loss']) == 200.0 # (170-150)*10

def test_delete_investment(populated_db):
    response = populated_db.delete('/api/investments/1')
    assert response.status_code == 200
    assert 'message' in response.get_json()

    response = populated_db.get('/api/investments')
    data = response.get_json()
    assert len(data) == 1

# ============================================================================
# DASHBOARD & ANALYTICS TESTS
# ============================================================================

def test_get_dashboard_data(populated_db):
    response = populated_db.get('/api/dashboard')
    assert response.status_code == 200
    data = response.get_json()
    assert 'financial_summary' in data
    assert 'investment_summary' in data
    assert 'expense_breakdown' in data
    assert 'recent_transactions' in data
    assert 'budget_progress' in data
    assert 'alerts' in data
    assert data['financial_summary']['total_income'] == 2000.00 # From t2
    # Food: -50, Rent: -1000 => total expenses: 1050
    assert data['financial_summary']['total_expenses'] == 1050.00
    assert data['financial_summary']['net_income'] == 950.00
    assert data['investment_summary']['total_value'] == (10*160) + (0.5*2200) # 1600 + 1100 = 2700
    assert data['investment_summary']['total_gain_loss'] == (10*10) + (0.5*200) # 100 + 100 = 200
    assert len(data['expense_breakdown']) > 0
    assert len(data['recent_transactions']) > 0

def test_get_spending_trends(populated_db):
    response = populated_db.get('/api/analytics/spending-trends?months=1')
    assert response.status_code == 200
    data = response.get_json()
    assert 'trends' in data
    assert len(data['trends']) >= 1 # At least current month
    # Assuming current month has food expenses of 50
    current_month_spending = sum(item['total'] for item in data['trends'] if item['month'] == date.today().strftime('%Y-%m'))
    assert current_month_spending == 50.0

def test_get_investment_performance(populated_db):
    response = populated_db.get('/api/analytics/investment-performance')
    assert response.status_code == 200
    data = response.get_json()
    assert 'performance_data' in data
    assert len(data['performance_data']) == 2
    assert data['performance_data'][0]['asset_name'] == 'ETH' # ETH has higher percentage gain
    assert data['performance_data'][0]['gain_loss_percentage'] == 10.0 # (2200-2000)/2000 * 100 = 10%
    assert data['performance_data'][1]['asset_name'] == 'AAPL'
    assert data['performance_data'][1]['gain_loss_percentage'] == (10/150)*100 # (160-150)/150 * 100 = 6.66% approx

# ============================================================================
# FEATURE 1004 - BUDGET ANALYTICS TESTS
# ============================================================================

def test_budget_variance_endpoint(populated_db):
    # Ensure budgets exist for expense categories
    populated_db.put('/api/categories/1', json={'budget_limit': 100.0})  # Food
    populated_db.put('/api/categories/3', json={'budget_limit': 1000.0}) # Rent

    # Use a period that covers both transactions
    from datetime import date, timedelta
    start_date = (date.today() - timedelta(days=40)).strftime('%Y-%m-%d')
    end_date = date.today().strftime('%Y-%m-%d')

    response = populated_db.get(f'/api/analytics/budget-variance?start_date={start_date}&end_date={end_date}')
    assert response.status_code == 200
    data = response.get_json()
    assert 'categories' in data and 'summary' in data
    # Expect at least Food and Rent present
    names = [c['category_name'] for c in data['categories']]
    assert 'Food' in names
    assert 'Rent' in names

def test_spending_patterns_endpoint(populated_db):
    response = populated_db.get('/api/analytics/spending-patterns?days=30')
    assert response.status_code == 200
    data = response.get_json()
    assert 'top_categories' in data
    assert isinstance(data['top_categories'], list)

def test_forecasts_endpoint(populated_db):
    # Add budgets to enable forecasts
    populated_db.put('/api/categories/1', json={'budget_limit': 120.0})  # Food
    response = populated_db.get('/api/analytics/forecasts')
    assert response.status_code == 200
    data = response.get_json()
    assert 'forecasts' in data
    # At least one forecast row may exist if budgets are set
    assert isinstance(data['forecasts'], list)

def test_recommendations_endpoint(populated_db):
    # Configure budget tightness to trigger recommendations
    populated_db.put('/api/categories/1', json={'budget_limit': 60.0})
    # Add extra expense to tighten pace
    extra_tx = {
        'date': date.today().strftime('%Y-%m-%d'),
        'amount': 20.0,
        'category_id': 1,
        'description': 'Extra food expense',
        'type': 'expense'
    }
    populated_db.post('/api/transactions', json=extra_tx)

    response = populated_db.get('/api/analytics/recommendations')
    assert response.status_code == 200
    data = response.get_json()
    assert 'recommendations' in data
    assert isinstance(data['recommendations'], list)

def test_export_budget_variance_csv(populated_db):
    # Ensure budget for Food
    populated_db.put('/api/categories/1', json={'budget_limit': 100.0})
    response = populated_db.get('/api/analytics/export?report=budget_variance&format=csv')
    assert response.status_code == 200
    # In Flask test client, response.data is bytes
    csv_text = response.data.decode('utf-8')
    assert 'Category' in csv_text
    assert 'Food' in csv_text