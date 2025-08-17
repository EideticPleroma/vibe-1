import React, { useState, useEffect } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { TrendingUp, TrendingDown, DollarSign, BarChart3 } from 'lucide-react';
import { analyticsApi, formatCurrency, formatPercentage } from '../services/api';
import { SpendingTrends, InvestmentPerformance } from '../types';

const Analytics: React.FC = () => {
  const [spendingTrends, setSpendingTrends] = useState<SpendingTrends | null>(null);
  const [investmentPerformance, setInvestmentPerformance] = useState<InvestmentPerformance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMonths, setSelectedMonths] = useState(6);

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedMonths]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const [trends, performance] = await Promise.all([
        analyticsApi.getSpendingTrends(selectedMonths),
        analyticsApi.getInvestmentPerformance()
      ]);
      setSpendingTrends(trends);
      setInvestmentPerformance(performance);
    } catch (err) {
      setError('Failed to load analytics data');
      console.error('Analytics error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="lg:ml-64 p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="h-80 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="lg:ml-64 p-6">
        <div className="text-center py-12">
          <div className="text-red-500 text-xl mb-4">{error}</div>
          <button 
            onClick={() => fetchAnalyticsData()} 
            className="btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return '$' + value.toLocaleString();
          }
        }
      }
    }
  };

  // Spending trends chart data
  const spendingTrendsData = spendingTrends ? {
    labels: spendingTrends.trends.map(item => item.month),
    datasets: [{
      label: 'Monthly Spending',
      data: spendingTrends.trends.map(item => item.total),
      borderColor: '#ef4444',
      backgroundColor: 'rgba(239, 68, 68, 0.1)',
      tension: 0.4,
      fill: true,
    }],
  } : null;

  // Investment performance chart data
  const investmentPerformanceData = investmentPerformance ? {
    labels: investmentPerformance.performance_data.map(item => item.asset_name),
    datasets: [{
      label: 'Total Invested',
      data: investmentPerformance.performance_data.map(item => item.total_invested),
      backgroundColor: 'rgba(59, 130, 246, 0.8)',
      borderColor: '#3b82f6',
      borderWidth: 1,
    }, {
      label: 'Current Value',
      data: investmentPerformance.performance_data.map(item => item.current_value),
      backgroundColor: 'rgba(34, 197, 94, 0.8)',
      borderColor: '#22c55e',
      borderWidth: 1,
    }],
  } : null;

  // Investment type distribution
  const investmentTypeData = investmentPerformance ? {
    labels: ['Stocks', 'Crypto', 'Bonds', 'ETFs', 'Other'],
    datasets: [{
      data: [
        investmentPerformance.performance_data.filter(item => item.asset_type === 'stock').length,
        investmentPerformance.performance_data.filter(item => item.asset_type === 'crypto').length,
        investmentPerformance.performance_data.filter(item => item.asset_type === 'bond').length,
        investmentPerformance.performance_data.filter(item => item.asset_type === 'etf').length,
        investmentPerformance.performance_data.filter(item => !['stock', 'crypto', 'bond', 'etf'].includes(item.asset_type)).length,
      ],
      backgroundColor: [
        '#3b82f6',
        '#8b5cf6',
        '#10b981',
        '#f59e0b',
        '#6b7280',
      ],
      borderColor: [
        '#2563eb',
        '#7c3aed',
        '#059669',
        '#d97706',
        '#4b5563',
      ],
      borderWidth: 2,
    }],
  } : null;

  return (
    <div className="lg:ml-64 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics</h1>
        <p className="text-gray-600">Deep insights into your spending patterns and investment performance</p>
      </div>

      {/* Spending Trends Section */}
      <div className="card mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Spending Trends</h2>
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Time Period:</label>
            <select
              value={selectedMonths}
              onChange={(e) => setSelectedMonths(parseInt(e.target.value))}
              className="input w-32"
            >
              <option value={3}>3 months</option>
              <option value={6}>6 months</option>
              <option value={12}>12 months</option>
            </select>
          </div>
        </div>
        
        {spendingTrendsData ? (
          <div className="h-80">
            <Line data={spendingTrendsData} options={chartOptions} />
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            No spending data available for the selected period
          </div>
        )}
      </div>

      {/* Investment Performance Section */}
      {investmentPerformance && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Performance Bar Chart */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Performance</h3>
            <div className="h-80">
              {investmentPerformanceData ? (
                <Bar data={investmentPerformanceData} options={chartOptions} />
              ) : (
                <div className="text-center py-12 text-gray-500">
                  No investment data available
                </div>
              )}
            </div>
          </div>

          {/* Investment Type Distribution */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Distribution</h3>
            <div className="h-80">
              {investmentTypeData ? (
                <Doughnut data={investmentTypeData} options={chartOptions} />
              ) : (
                <div className="text-center py-12 text-gray-500">
                  No investment data available
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Investment Performance Table */}
      {investmentPerformance && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Performance</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Asset
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Invested
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Gain/Loss
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Performance
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {investmentPerformance.performance_data.map((item) => (
                  <tr key={item.asset_name} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {item.asset_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        item.asset_type === 'stock' ? 'bg-blue-100 text-blue-800' :
                        item.asset_type === 'crypto' ? 'bg-purple-100 text-purple-800' :
                        item.asset_type === 'bond' ? 'bg-green-100 text-green-800' :
                        item.asset_type === 'etf' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {item.asset_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(item.total_invested)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(item.current_value)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {item.is_profitable ? (
                          <TrendingUp className="h-4 w-4 text-success-500 mr-1" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-danger-500 mr-1" />
                        )}
                        <span className={`text-sm font-medium ${
                          item.is_profitable ? 'text-success-600' : 'text-danger-600'
                        }`}>
                          {formatCurrency(item.total_gain_loss)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${
                        item.is_profitable ? 'text-success-600' : 'text-danger-600'
                      }`}>
                        {formatPercentage(item.gain_loss_percentage)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Summary Statistics */}
      {investmentPerformance && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="card text-center">
            <div className="p-3 bg-primary-100 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
              <BarChart3 className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Investments</h3>
            <p className="text-3xl font-bold text-primary-600">
              {investmentPerformance.total_investments}
            </p>
          </div>

          <div className="card text-center">
            <div className="p-3 bg-success-100 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
              <TrendingUp className="h-8 w-8 text-success-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Profitable Assets</h3>
            <p className="text-3xl font-bold text-success-600">
              {investmentPerformance.performance_data.filter(item => item.is_profitable).length}
            </p>
          </div>

          <div className="card text-center">
            <div className="p-3 bg-warning-100 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
              <DollarSign className="h-8 w-8 text-warning-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Best Performer</h3>
            <p className="text-lg font-medium text-warning-600">
              {investmentPerformance.performance_data.length > 0 
                ? investmentPerformance.performance_data[0].asset_name 
                : 'N/A'
              }
            </p>
            <p className="text-sm text-gray-500">
              {investmentPerformance.performance_data.length > 0 
                ? formatPercentage(investmentPerformance.performance_data[0].gain_loss_percentage)
                : ''
              }
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analytics;
