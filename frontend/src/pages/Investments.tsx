import React, { useState, useEffect, useCallback } from 'react';
import { Plus, TrendingUp, TrendingDown, Edit, Trash2, DollarSign, X } from 'lucide-react';
import { investmentsApi, formatCurrency, formatPercentage, formatDate } from '../services/api.ts';
import { Investment, InvestmentFormData } from '../types';

const Investments: React.FC = () => {
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [editingInvestment, setEditingInvestment] = useState<Investment | null>(null);
  const [formData, setFormData] = useState<InvestmentFormData>({
    asset_name: '',
    asset_type: 'stock',
    quantity: 0,
    purchase_price: 0,
    current_price: 0,
    purchase_date: new Date().toISOString().split('T')[0],
  });

  const fetchInvestments = useCallback(async () => {
    try {
      setLoading(true);
      const investmentsData = await investmentsApi.getAll();
      setInvestments(investmentsData);
    } catch (err) {
      setError('Failed to load investments');
      console.error('Investments error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInvestments();
  }, [fetchInvestments]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.asset_name.trim() || formData.quantity <= 0 || formData.purchase_price <= 0) return;

    try {
      if (editingInvestment) {
        await investmentsApi.update(editingInvestment.id, formData);
      } else {
        await investmentsApi.create(formData);
      }
      setShowModal(false);
      setEditingInvestment(null);
      resetForm();
      fetchInvestments();
    } catch (err) {
      console.error('Investment operation error:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this investment?')) {
      try {
        await investmentsApi.delete(id);
        fetchInvestments();
      } catch (err) {
        console.error('Delete investment error:', err);
      }
    }
  };

  const handleEdit = (investment: Investment) => {
    setEditingInvestment(investment);
    setFormData({
      asset_name: investment.asset_name,
      asset_type: investment.asset_type,
      quantity: investment.quantity,
      purchase_price: investment.purchase_price,
      current_price: investment.current_price,
      purchase_date: investment.purchase_date,
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      asset_name: '',
      asset_type: 'stock',
      quantity: 0,
      purchase_price: 0,
      current_price: 0,
      purchase_date: new Date().toISOString().split('T')[0],
    });
  };

  const openCreateModal = () => {
    setEditingInvestment(null);
    resetForm();
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingInvestment(null);
    resetForm();
  };

  const getTotalPortfolioValue = () => {
    return investments.reduce((sum, inv) => sum + inv.current_value, 0);
  };

  const getTotalPortfolioGainLoss = () => {
    return investments.reduce((sum, inv) => sum + inv.total_gain_loss, 0);
  };

  if (loading) {
    return (
      <div className="lg:ml-64 p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="lg:ml-64 p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Investments</h1>
          <p className="text-gray-600">Track your investment portfolio and performance</p>
        </div>
        <button
          onClick={openCreateModal}
          className="btn-primary flex items-center space-x-2 mt-4 sm:mt-0"
        >
          <Plus className="h-5 w-5" />
          <span>Add Investment</span>
        </button>
      </div>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Portfolio Value</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(getTotalPortfolioValue())}
              </p>
            </div>
            <div className="p-3 bg-primary-100 rounded-full">
              <DollarSign className="h-6 w-6 text-primary-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Gain/Loss</p>
              <p className={`text-2xl font-bold ${
                getTotalPortfolioGainLoss() >= 0 ? 'text-success-600' : 'text-danger-600'
              }`}>
                {formatCurrency(getTotalPortfolioGainLoss())}
              </p>
            </div>
            <div className={`p-3 rounded-full ${
              getTotalPortfolioGainLoss() >= 0 ? 'bg-success-100' : 'bg-danger-100'
            }`}>
              {getTotalPortfolioGainLoss() >= 0 ? (
                <TrendingUp className="h-6 w-6 text-success-600" />
              ) : (
                <TrendingDown className="h-6 w-6 text-danger-600" />
              )}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Investments</p>
              <p className="text-2xl font-bold text-gray-900">{investments.length}</p>
            </div>
            <div className="p-3 bg-warning-100 rounded-full">
              <TrendingUp className="h-6 w-6 text-warning-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Investments List */}
      <div className="card">
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
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Purchase Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Current Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Gain/Loss
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {investments.map((investment) => (
                <tr key={investment.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {investment.asset_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        Purchased {formatDate(investment.purchase_date)}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      investment.asset_type === 'stock' ? 'bg-blue-100 text-blue-800' :
                      investment.asset_type === 'crypto' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {investment.asset_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {investment.quantity}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatCurrency(investment.purchase_price)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatCurrency(investment.current_price)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {formatCurrency(investment.current_value)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm">
                      <div className={`font-medium ${
                        investment.is_profitable ? 'text-success-600' : 'text-danger-600'
                      }`}>
                        {formatCurrency(investment.total_gain_loss)}
                      </div>
                      <div className={`text-xs ${
                        investment.is_profitable ? 'text-success-500' : 'text-danger-500'
                      }`}>
                        {formatPercentage(investment.gain_loss_percentage)}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => handleEdit(investment)}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(investment.id)}
                        className="text-danger-600 hover:text-danger-900"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Investment Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div
              className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
              onClick={closeModal}
            />

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    {editingInvestment ? 'Edit Investment' : 'Add Investment'}
                  </h3>
                  <button
                    onClick={closeModal}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-6 w-6" />
                  </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Asset Name */}
                  <div>
                    <label className="label">Asset Name</label>
                    <input
                      type="text"
                      value={formData.asset_name}
                      onChange={(e) => setFormData(prev => ({ ...prev, asset_name: e.target.value }))}
                      className="input"
                      placeholder="e.g., AAPL, Bitcoin, etc."
                      required
                    />
                  </div>

                  {/* Asset Type */}
                  <div>
                    <label className="label">Asset Type</label>
                    <select
                      value={formData.asset_type}
                      onChange={(e) => setFormData(prev => ({ ...prev, asset_type: e.target.value }))}
                      className="input"
                    >
                      <option value="stock">Stock</option>
                      <option value="crypto">Cryptocurrency</option>
                      <option value="bond">Bond</option>
                      <option value="etf">ETF</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  {/* Quantity */}
                  <div>
                    <label className="label">Quantity</label>
                    <input
                      type="number"
                      step="0.000001"
                      min="0.000001"
                      value={formData.quantity}
                      onChange={(e) => setFormData(prev => ({ ...prev, quantity: parseFloat(e.target.value) || 0 }))}
                      className="input"
                      placeholder="0.00"
                      required
                    />
                  </div>

                  {/* Purchase Price */}
                  <div>
                    <label className="label">Purchase Price (per unit)</label>
                    <div className="relative">
                      <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                        $
                      </span>
                      <input
                        type="number"
                        step="0.01"
                        min="0.01"
                        value={formData.purchase_price}
                        onChange={(e) => setFormData(prev => ({ ...prev, purchase_price: parseFloat(e.target.value) || 0 }))}
                        className="input pl-8"
                        placeholder="0.00"
                        required
                      />
                    </div>
                  </div>

                  {/* Current Price */}
                  <div>
                    <label className="label">Current Price (per unit)</label>
                    <div className="relative">
                      <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                        $
                      </span>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        value={formData.current_price}
                        onChange={(e) => setFormData(prev => ({ ...prev, current_price: parseFloat(e.target.value) || 0 }))}
                        className="input pl-8"
                        placeholder="0.00"
                      />
                    </div>
                  </div>

                  {/* Purchase Date */}
                  <div>
                    <label className="label">Purchase Date</label>
                    <input
                      type="date"
                      value={formData.purchase_date}
                      onChange={(e) => setFormData(prev => ({ ...prev, purchase_date: e.target.value }))}
                      className="input"
                      required
                    />
                  </div>

                  {/* Submit Button */}
                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={closeModal}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn-primary"
                      disabled={!formData.asset_name.trim() || formData.quantity <= 0 || formData.purchase_price <= 0}
                    >
                      {editingInvestment ? 'Update' : 'Create'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Investments;
