#!/usr/bin/env python3
"""
Unit tests for Intelligent Alert System (Feature 1003)
"""

import unittest
import json
from datetime import date
from flask import Flask

from models import db, Category, Transaction, Alert, NotificationPreference
from routes import api


class TestIntelligentAlerts(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.register_blueprint(api)

        db.init_app(self.app)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Create a category and some transactions
            groceries = Category(
                name='Groceries', type='expense', color='#FF6B6B',
                budget_limit=500.0, budget_period='monthly', budget_type='fixed'
            )
            db.session.add(groceries)
            db.session.commit()

            # Add a normal transaction
            t = Transaction(
                date=date.today(), amount=-40.0, category_id=groceries.id,
                description='Weekly groceries', type='expense'
            )
            db.session.add(t)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_alert_preferences_get_and_update(self):
        with self.app.app_context():
            # Get defaults (auto-created)
            res = self.client.get('/api/alerts/preferences')
            self.assertEqual(res.status_code, 200)
            prefs = json.loads(res.data)['preferences']
            self.assertIn('in_app_enabled', prefs)

            # Update prefs
            res = self.client.post('/api/alerts/preferences', json={
                'email_enabled': True,
                'quiet_hours_start': '22:00',
                'quiet_hours_end': '07:00'
            })
            self.assertEqual(res.status_code, 200)
            prefs = json.loads(res.data)['preferences']
            self.assertTrue(prefs['email_enabled'])
            self.assertEqual(prefs['quiet_hours_start'], '22:00')

    def test_create_list_dismiss_snooze_alerts(self):
        with self.app.app_context():
            # Create an alert
            res = self.client.post('/api/alerts', json={
                'type': 'budget_threshold',
                'message': 'Warning: Groceries exceeded 80% of budget',
                'severity': 'medium'
            })
            self.assertEqual(res.status_code, 201)
            alert = json.loads(res.data)
            alert_id = alert['id']

            # List alerts
            res = self.client.get('/api/alerts')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertGreaterEqual(data['counts']['total'], 1)

            # Snooze alert
            res = self.client.post(f'/api/alerts/{alert_id}/snooze', json={'hours': 1})
            self.assertEqual(res.status_code, 200)
            snoozed = json.loads(res.data)['alert']
            self.assertEqual(snoozed['status'], 'snoozed')

            # Snoozed alert should be excluded from default listing
            res = self.client.get('/api/alerts')
            self.assertEqual(res.status_code, 200)
            default_alerts = json.loads(res.data)['alerts']
            self.assertTrue(all(a['id'] != alert_id for a in default_alerts))

            # But appear when filtered by status=snoozed
            res = self.client.get('/api/alerts?status=snoozed')
            self.assertEqual(res.status_code, 200)
            snoozed_list = json.loads(res.data)['alerts']
            self.assertTrue(any(a['id'] == alert_id for a in snoozed_list))

            # Dismiss alert
            res = self.client.post(f'/api/alerts/{alert_id}/dismiss')
            self.assertEqual(res.status_code, 200)
            dismissed = json.loads(res.data)['alert']
            self.assertEqual(dismissed['status'], 'dismissed')

    def test_anomaly_detection(self):
        with self.app.app_context():
            cat = Category.query.filter_by(name='Groceries').first()

            # Detect anomaly for a very large expense
            res = self.client.post('/api/alerts/anomalies/detect', json={
                'category_id': cat.id,
                'amount': 1000.0,
                'multiplier': 5.0
            })
            self.assertEqual(res.status_code, 200)
            payload = json.loads(res.data)
            self.assertIn('is_anomaly', payload)

            # Should create an alert if anomaly
            if payload['is_anomaly']:
                self.assertIn('alert', payload)
                self.assertEqual(payload['alert']['type'], 'anomaly')


if __name__ == '__main__':
    unittest.main()


