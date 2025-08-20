import pytest
from app import create_app
from models import db


@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        with app.app_context():
            for table in reversed(db.metadata.sorted_tables):
                db.session.execute(table.delete())
            db.session.commit()
        yield client


def test_create_and_list_incomes(client):
    payload = {
        'amount': 3000.0,
        'type': 'salary',
        'frequency': 'monthly',
        'source_name': 'Main Salary',
        'is_bonus': False,
    }
    resp = client.post('/api/incomes', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['source_name'] == 'Main Salary'
    assert data['frequency'] == 'monthly'
    assert float(data['amount']) == 3000.0

    # List
    resp = client.get('/api/incomes')
    assert resp.status_code == 200
    items = resp.get_json()
    assert isinstance(items, list) and len(items) == 1


def test_update_income(client):
    # Create
    resp = client.post('/api/incomes', json={
        'amount': 1000.0,
        'type': 'freelance',
        'frequency': 'weekly',
        'source_name': 'Side Gig',
    })
    assert resp.status_code == 201
    inc = resp.get_json()

    # Update
    resp = client.put(f"/api/incomes/{inc['id']}", json={'amount': 1200.0, 'frequency': 'bi-weekly'})
    assert resp.status_code == 200
    updated = resp.get_json()
    assert float(updated['amount']) == 1200.0
    assert updated['frequency'] in ('bi-weekly', 'biweekly')


def test_delete_income(client):
    # Create
    resp = client.post('/api/incomes', json={
        'amount': 500.0,
        'frequency': 'weekly',
        'source_name': 'Part-time',
    })
    inc = resp.get_json()

    # Delete
    resp = client.delete(f"/api/incomes/{inc['id']}")
    assert resp.status_code == 200
    # Verify list empty
    resp = client.get('/api/incomes')
    assert resp.status_code == 200
    assert len(resp.get_json()) == 0


def test_dashboard_uses_configured_incomes_when_present(client):
    # Configure incomes: 3000 monthly + 500 weekly (approx 4.33 weeks per month)
    client.post('/api/incomes', json={'amount': 3000.0, 'frequency': 'monthly', 'source_name': 'Salary'})
    client.post('/api/incomes', json={'amount': 500.0, 'frequency': 'weekly', 'source_name': 'Freelance'})

    resp = client.get('/api/dashboard')
    assert resp.status_code == 200
    data = resp.get_json()
    expected_monthly = 3000.0 + 500.0 * 4.33
    assert pytest.approx(data['financial_summary']['total_income'], rel=1e-3) == expected_monthly


