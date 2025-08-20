#!/usr/bin/env python3
"""
Quick test script to verify the new advanced budget tracking endpoints are working
"""

import requests
import time
import sys

def test_endpoints():
    base_url = 'http://localhost:5000'

    # Test the new endpoints
    endpoints = [
        '/api/budget/progress/advanced',
        '/api/budget/trends/historical?months=3',
        '/api/budget/performance-score',
        '/api/budget/predictive-alerts'
    ]

    print("Testing advanced budget tracking endpoints...")
    print("=" * 50)

    for endpoint in endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=10)
            print(f'{endpoint}: {response.status_code}')

            if response.status_code == 200:
                data = response.json()
                print(f'  ✓ Success - Response keys: {list(data.keys())}')

                # Show some sample data
                if 'summary' in data:
                    summary = data['summary']
                    print(f'  - Categories tracked: {summary.get("categories_count", 0)}')
                    print(f'  - Average health score: {summary.get("average_health_score", 0):.1f}%')

                if 'performance' in data:
                    perf = data['performance']
                    print(f'  - Performance score: {perf.get("overall_score", 0):.1f}%')
                    print(f'  - Categories tracked: {perf.get("categories_tracked", 0)}')

                if 'alerts' in data:
                    alerts = data['alerts']
                    print(f'  - Total alerts: {len(alerts)}')

            else:
                print(f'  ✗ Error: {response.status_code} - {response.text[:100]}')

        except requests.exceptions.ConnectionError:
            print(f'{endpoint}: ✗ Connection Error - Is the server running?')
        except Exception as e:
            print(f'{endpoint}: ✗ Error - {e}')
        print()

if __name__ == '__main__':
    # Wait a moment for server to start if needed
    time.sleep(1)
    test_endpoints()
