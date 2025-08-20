import React, { useEffect, useMemo, useState } from 'react';
import { alertsApi, budgetApi, formatCurrency } from '../services/api';
import { AlertItem, AlertListResponse, NotificationPreferences } from '../types';
import { Alert, AlertTitle, AlertDescription } from '../components/ui/alert';

const severityBadgeClasses: Record<string, string> = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-blue-100 text-blue-700',
};

const Alerts: React.FC = () => {
  const [data, setData] = useState<AlertListResponse | null>(null);
  const [prefs, setPrefs] = useState<NotificationPreferences | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<{ status?: string; severity?: string; type?: string }>({ status: 'active' });

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [alerts, preferences] = await Promise.all([
        alertsApi.list(filters as any),
        alertsApi.getPreferences(),
      ]);
      setData(alerts);
      setPrefs(preferences.preferences);
    } catch (e: any) {
      setError(e?.message || 'Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(filters)]);

  const handleDismiss = async (alertId: number) => {
    await alertsApi.dismiss(alertId);
    fetchAll();
  };

  const handleSnooze = async (alertId: number, hours: number) => {
    await alertsApi.snooze(alertId, hours);
    fetchAll();
  };

  const updatePrefs = async (next: Partial<NotificationPreferences>) => {
    const res = await alertsApi.updatePreferences(next);
    setPrefs(res.preferences);
  };

  if (loading) {
    return (
      <div className="lg:ml-64 p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="lg:ml-64 p-6">
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

  const alerts = data?.alerts || [];

  return (
    <div className="lg:ml-64 p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Alerts</h1>
        <p className="text-gray-600">Manage intelligent alerts, preferences, and history</p>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
          <div className="flex gap-2">
            <select
              value={filters.status || ''}
              onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value || undefined }))}
              className="input"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="snoozed">Snoozed</option>
              <option value="dismissed">Dismissed</option>
            </select>
            <select
              value={filters.severity || ''}
              onChange={(e) => setFilters((f) => ({ ...f, severity: e.target.value || undefined }))}
              className="input"
            >
              <option value="">All Severity</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
            <input
              placeholder="Type (e.g., anomaly)"
              className="input"
              value={filters.type || ''}
              onChange={(e) => setFilters((f) => ({ ...f, type: e.target.value || undefined }))}
            />
          </div>
        </div>

        {alerts.length === 0 ? (
          <div className="text-gray-500">No alerts found</div>
        ) : (
          <div className="space-y-3">
            {alerts.map((a) => (
              <Alert key={a.id} className="flex items-start justify-between">
                <div>
                  <AlertTitle>
                    <span className={`px-2 py-0.5 rounded mr-2 text-xs ${severityBadgeClasses[a.severity] || ''}`}>
                      {a.severity.toUpperCase()}
                    </span>
                    {a.type} {a.category_name ? `• ${a.category_name}` : ''}
                  </AlertTitle>
                  <AlertDescription>
                    {a.message}
                  </AlertDescription>
                  {a.metadata && a.metadata.predicted_overspend && (
                    <div className="text-xs text-gray-600 mt-1">
                      Predicted overspend: {formatCurrency(a.metadata.predicted_overspend)}
                    </div>
                  )}
                  {a.snooze_until && (
                    <div className="text-xs text-gray-500 mt-1">Snoozed until {new Date(a.snooze_until).toLocaleString()}</div>
                  )}
                </div>
                <div className="flex gap-2">
                  {a.status !== 'dismissed' && (
                    <button className="btn-secondary" onClick={() => handleDismiss(a.id)}>Dismiss</button>
                  )}
                  {a.status !== 'snoozed' && (
                    <button className="btn-primary" onClick={() => handleSnooze(a.id, 24)}>Snooze 1d</button>
                  )}
                </div>
              </Alert>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h3>
        {prefs && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={!!prefs.in_app_enabled}
                onChange={(e) => updatePrefs({ in_app_enabled: e.target.checked })}
              />
              In-app notifications
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={!!prefs.email_enabled}
                onChange={(e) => updatePrefs({ email_enabled: e.target.checked })}
              />
              Email
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={!!prefs.sms_enabled}
                onChange={(e) => updatePrefs({ sms_enabled: e.target.checked })}
              />
              SMS
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={!!prefs.push_enabled}
                onChange={(e) => updatePrefs({ push_enabled: e.target.checked })}
              />
              Push
            </label>
          </div>
        )}
      </div>
    </div>
  );
};

export default Alerts;


