import React, { useState, useEffect, useCallback } from 'react';
import { Doughnut, Line } from 'react-chartjs-2';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  PiggyBank,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { dashboardApi, analyticsApi, formatCurrency, formatPercentage } from '../services/api.ts';
import { DashboardData, SpendingTrends } from '../types';

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [spendingTrends, setSpendingTrends] = useState<SpendingTrends | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const [dashboard, trends] = await Promise.all([
        dashboardApi.getData(),
        analyticsApi.getSpendingTrends(6)
      ]);
      setDashboardData(dashboard);
      setSpendingTrends(trends);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  if (loading) {
    return (
      <div className="lg:ml-64 p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="h-80 bg-gray-200 rounded"></div>
            ))}
          </div>
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
            onClick={() => window.location.reload()} 
            className="btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData) return null;

  const { financial_summary, investment_summary, expense_breakdown, recent_transactions } = dashboardData;

  // Prepare chart data
  const expenseChartData = {
    labels: expense_breakdown.map(item => item.name),
    datasets: [{
      data: expense_breakdown.map(item => item.total),
      backgroundColor: expense_breakdown.map(item => item.color),
      borderColor: expense_breakdown.map(item => item.color),
      borderWidth: 2,
    }],
  };

  const spendingTrendsData = spendingTrends ? {
    labels: spendingTrends.trends.map(item => item.month),
    datasets: [{
      label: 'Monthly Spending',
      data: spendingTrends.trends.map(item => item.total),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      fill: true,
    }],
  } : null;

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
  };

  return (
    <div className="lg:ml-64 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Overview of your financial health and recent activity</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Income */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Income</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(financial_summary.total_income)}
              </p>
            </div>
            <div className="p-3 bg-success-100 rounded-full">
              <TrendingUp className="h-6 w-6 text-success-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <ArrowUpRight className="h-4 w-4 text-success-500 mr-1" />
            <span className="text-success-600 font-medium">This month</span>
          </div>
        </div>

        {/* Total Expenses */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Expenses</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(financial_summary.total_expenses)}
              </p>
            </div>
            <div className="p-3 bg-danger-100 rounded-full">
              <TrendingDown className="h-6 w-6 text-danger-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <ArrowDownRight className="h-4 w-4 text-danger-500 mr-1" />
            <span className="text-danger-600 font-medium">This month</span>
          </div>
        </div>

        {/* Net Income */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Net Income</p>
              <p className={`text-2xl font-bold ${
                financial_summary.net_income >= 0 ? 'text-success-600' : 'text-danger-600'
              }`}>
                {formatCurrency(financial_summary.net_income)}
              </p>
            </div>
            <div className="p-3 bg-primary-100 rounded-full">
              <DollarSign className="h-6 w-6 text-primary-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className={`font-medium ${
              financial_summary.net_income >= 0 ? 'text-success-600' : 'text-danger-600'
            }`}>
              {financial_summary.net_income >= 0 ? 'Positive' : 'Negative'} cash flow
            </span>
          </div>
        </div>

        {/* Investment Value */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Investment Value</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(investment_summary.total_value)}
              </p>
            </div>
            <div className="p-3 bg-warning-100 rounded-full">
              <PiggyBank className="h-6 w-6 text-warning-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className={`font-medium ${
              investment_summary.total_gain_loss >= 0 ? 'text-success-600' : 'text-danger-600'
            }`}>
              {formatPercentage(investment_summary.total_gain_loss)}
            </span>
          </div>
        </div>
      </div>

      {/* Charts and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Expense Breakdown Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Expense Breakdown</h3>
          <div className="h-80">
            <Doughnut data={expenseChartData} options={chartOptions} />
          </div>
        </div>

        {/* Spending Trends Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Spending Trends</h3>
          <div className="h-80">
            {spendingTrendsData ? (
              <Line data={spendingTrendsData} options={chartOptions} />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                No spending data available
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Recent Transactions</h3>
          <a href="/transactions" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
            View all →
          </a>
        </div>
        
        <div className="space-y-4">
          {recent_transactions.length > 0 ? (
            recent_transactions.map((transaction) => (
              <div key={transaction.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: transaction.category_color || '#6b7280' }}
                  />
                  <div>
                    <p className="font-medium text-gray-900">{transaction.description}</p>
                    <p className="text-sm text-gray-500">
                      {transaction.category_name} • {new Date(transaction.date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-semibold ${
                    transaction.is_income ? 'text-success-600' : 'text-danger-600'
                  }`}>
                    {transaction.is_income ? '+' : '-'}{formatCurrency(transaction.absolute_amount)}
                  </p>
                  <p className="text-sm text-gray-500">{transaction.type}</p>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No recent transactions
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
