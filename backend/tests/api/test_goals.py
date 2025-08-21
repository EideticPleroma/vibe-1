import pytest
from datetime import date, timedelta
from app import create_app, db
from models import BudgetGoal, Category, Transaction

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def sample_category(client):
    with client.application.app_context():
        category = Category(
            name='Savings',
            type='income',
            color='#00ff00'
        )
        db.session.add(category)
        db.session.commit()
        return category.id  # Return id instead

def test_create_goal(client):
    goal_data = {
        'name': 'Vacation Fund',
        'target_amount': 5000.0,
        'deadline': (date.today() + timedelta(days=365)).isoformat()
    }
    response = client.post('/api/goals', json=goal_data)
    assert response.status_code == 201
    data = response.json
    assert data['name'] == goal_data['name']
    assert data['target_amount'] == goal_data['target_amount']
    assert data['current_amount'] == 0.0
    assert data['deadline'] == goal_data['deadline']

def test_get_goals(client):
    # Create a goal
    client.post('/api/goals', json={
        'name': 'Test Goal',
        'target_amount': 1000.0
    })
    response = client.get('/api/goals')
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]['name'] == 'Test Goal'

def test_update_goal(client):
    create_response = client.post('/api/goals', json={
        'name': 'Old Name',
        'target_amount': 1000.0
    })
    goal_id = create_response.json['id']

    update_data = {'name': 'New Name', 'target_amount': 2000.0}
    response = client.put(f'/api/goals/{goal_id}', json=update_data)
    assert response.status_code == 200
    data = response.json
    assert data['name'] == 'New Name'
    assert data['target_amount'] == 2000.0

def test_delete_goal(client):
    create_response = client.post('/api/goals', json={
        'name': 'To Delete',
        'target_amount': 1000.0
    })
    goal_id = create_response.json['id']

    response = client.delete(f'/api/goals/{goal_id}')
    assert response.status_code == 200

    # Verify deletion
    response = client.get(f'/api/goals/{goal_id}')
    assert response.status_code == 404

def test_allocate_category(client, sample_category):
    create_response = client.post('/api/goals', json={
        'name': 'Test Goal',
        'target_amount': 1000.0
    })
    goal_id = create_response.json['id']

    response = client.post(f'/api/goals/{goal_id}/allocate-category', json={'category_id': sample_category})
    assert response.status_code == 200
    data = response.json
    assert len(data['categories']) == 1
    assert data['categories'][0]['id'] == sample_category

def test_update_progress(client, sample_category):
    # Create goal and allocate category
    create_response = client.post('/api/goals', json={
        'name': 'Test Goal',
        'target_amount': 1000.0
    })
    goal_id = create_response.json['id']

    client.post(f'/api/goals/{goal_id}/allocate-category', json={'category_id': sample_category})

    # Add a transaction
    with client.application.app_context():
        transaction = Transaction(
            date=date.today(),
            amount=500.0,
            category_id=sample_category,
            type='income',
            description='Test savings'
        )
        db.session.add(transaction)
        db.session.commit()

    # Update progress
    response = client.post(f'/api/goals/{goal_id}/update-progress')
    assert response.status_code == 200
    data = response.json
    assert data['current_amount'] == 500.0
    assert data['progress_percentage'] == 50.0
