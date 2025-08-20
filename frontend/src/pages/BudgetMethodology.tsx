import React, { useState, useEffect } from 'react';
import {
  Target,
  Calculator,
  Settings,
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  BarChart3,
  RefreshCw,
  Play,
  PieChart,
  Layers
} from 'lucide-react';

// Import UI components
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';

import {
  BudgetMethodology,
  BudgetMethodologyFormData,
  MethodologyCalculationResult,
  MethodologyRecommendation,
  UserFinancialProfile,
  MethodologyComparison,
  ZeroBasedCalculationResult,
  PercentageBasedCalculationResult,
  EnvelopeCalculationResult
} from '../types';
import {
  budgetMethodologyApi,
  formatCurrency,
  handleApiError,
} from '../services/api';

const BudgetMethodologyPage: React.FC = () => {
  const [methodologies, setMethodologies] = useState<BudgetMethodology[]>([]);
  const [activeMethodology, setActiveMethodology] = useState<BudgetMethodology | null>(null);
  const [calculationResult, setCalculationResult] = useState<MethodologyCalculationResult | null>(null);
  const [recommendations, setRecommendations] = useState<MethodologyRecommendation[]>([]);
  const [userProfile, setUserProfile] = useState<UserFinancialProfile | null>(null);
  const [comparisons, setComparisons] = useState<MethodologyComparison[]>([]);

  const [loading, setLoading] = useState(true);
  const [calculationLoading, setCalculationLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedMethodology, setSelectedMethodology] = useState<BudgetMethodology | null>(null);
  const [isCalculationDialogOpen, setIsCalculationDialogOpen] = useState(false);
  const [totalIncome, setTotalIncome] = useState<number>(0);

  useEffect(() => {
    loadMethodologyData();
  }, []);

  const loadMethodologyData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [methodologiesData, activeData, recommendationsData] = await Promise.all([
        budgetMethodologyApi.getAll(),
        budgetMethodologyApi.getActive(),
        budgetMethodologyApi.getRecommendations()
      ]);

      setMethodologies(methodologiesData);
      setActiveMethodology(activeData);
      setRecommendations(recommendationsData.recommendations);
      setUserProfile(recommendationsData.user_profile);
    } catch (err) {
      setError(handleApiError(err as any));
    } finally {
      setLoading(false);
    }
  };

  const handleActivateMethodology = async (methodology: BudgetMethodology) => {
    try {
      await budgetMethodologyApi.activate(methodology.id);
      await loadMethodologyData();
    } catch (err) {
      setError(handleApiError(err as any));
    }
  };

  const handleCalculateMethodology = async (methodology: BudgetMethodology) => {
    try {
      setCalculationLoading(true);
      const response = await budgetMethodologyApi.calculate(methodology.id, {
        total_income: totalIncome || undefined
      });
      setCalculationResult(response.calculation_result);
      setIsCalculationDialogOpen(true);
    } catch (err) {
      setError(handleApiError(err as any));
    } finally {
      setCalculationLoading(false);
    }
  };

  const handleApplyMethodology = async (methodology: BudgetMethodology, autoUpdate: boolean = false) => {
    try {
      setCalculationLoading(true);
      await budgetMethodologyApi.apply(methodology.id, {
        total_income: totalIncome || undefined,
        auto_update: autoUpdate
      });
      setIsCalculationDialogOpen(false);
      // Refresh data if auto-updated
      if (autoUpdate) {
        await loadMethodologyData();
      }
    } catch (err) {
      setError(handleApiError(err as any));
    } finally {
      setCalculationLoading(false);
    }
  };

  const handleCompareMethodologies = async () => {
    try {
      const selectedIds = methodologies
        .filter(m => m.methodology_type !== activeMethodology?.methodology_type)
        .slice(0, 3)
        .map(m => m.id);

      if (activeMethodology) {
        selectedIds.unshift(activeMethodology.id);
      }

      const response = await budgetMethodologyApi.compare({
        methodology_ids: selectedIds,
        total_income: totalIncome || undefined
      });
      setComparisons(response.comparisons);
    } catch (err) {
      setError(handleApiError(err as any));
    }
  };

  const getMethodologyIcon = (type: string) => {
    switch (type) {
      case 'zero_based': return <Target className="w-5 h-5" />;
      case 'percentage_based': return <PieChart className="w-5 h-5" />;
      case 'envelope': return <Layers className="w-5 h-5" />;
      default: return <Calculator className="w-5 h-5" />;
    }
  };

  const getMethodologyColor = (type: string) => {
    switch (type) {
      case 'zero_based': return 'text-blue-600 bg-blue-100';
      case 'percentage_based': return 'text-green-600 bg-green-100';
      case 'envelope': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const renderCalculationResult = () => {
    if (!calculationResult) return null;

    switch (calculationResult.methodology) {
      case 'Zero-Based Budgeting':
        const zeroResult = calculationResult as ZeroBasedCalculationResult;
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="p-3 bg-blue-50 rounded">
                <div className="font-medium text-blue-900">Total Income</div>
                <div className="text-lg font-bold text-blue-600">{formatCurrency(zeroResult.total_income)}</div>
              </div>
              <div className="p-3 bg-green-50 rounded">
                <div className="font-medium text-green-900">Total Allocated</div>
                <div className="text-lg font-bold text-green-600">{formatCurrency(zeroResult.total_allocated)}</div>
              </div>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">Allocations by Priority</h4>
              {zeroResult.allocations.map((allocation, index) => (
                <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <div>
                    <span className="font-medium">{allocation.category_name}</span>
                    <Badge variant="outline" className="ml-2 text-xs">{allocation.priority}</Badge>
                  </div>
                  <div className="text-right">
                    <div className="font-bold">{formatCurrency(allocation.allocated_amount)}</div>
                    <div className="text-xs text-gray-500">{allocation.percentage_of_income.toFixed(1)}%</div>
                  </div>
                </div>
              ))}
            </div>

            {zeroResult.unallocated > 0 && (
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                <div className="font-medium text-yellow-800">Unallocated: {formatCurrency(zeroResult.unallocated)}</div>
              </div>
            )}
          </div>
        );

      case (calculationResult.methodology.includes('Rule') ? calculationResult.methodology : ''):
        const percentageResult = calculationResult as PercentageBasedCalculationResult;
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="p-3 bg-blue-50 rounded">
                <div className="font-medium text-blue-900">Needs</div>
                <div className="text-lg font-bold text-blue-600">{formatCurrency(percentageResult.category_breakdown.needs.budget)}</div>
                <div className="text-xs text-blue-500">Allocated: {formatCurrency(percentageResult.category_breakdown.needs.allocated)}</div>
              </div>
              <div className="p-3 bg-green-50 rounded">
                <div className="font-medium text-green-900">Wants</div>
                <div className="text-lg font-bold text-green-600">{formatCurrency(percentageResult.category_breakdown.wants.budget)}</div>
                <div className="text-xs text-green-500">Allocated: {formatCurrency(percentageResult.category_breakdown.wants.allocated)}</div>
              </div>
              <div className="p-3 bg-purple-50 rounded">
                <div className="font-medium text-purple-900">Savings</div>
                <div className="text-lg font-bold text-purple-600">{formatCurrency(percentageResult.category_breakdown.savings.budget)}</div>
                <div className="text-xs text-purple-500">Allocated: {formatCurrency(percentageResult.category_breakdown.savings.allocated)}</div>
              </div>
            </div>

            <div className="space-y-3">
              {Object.entries(percentageResult.category_breakdown).map(([type, breakdown]) => (
                <div key={type} className="space-y-2">
                  <h4 className="font-medium capitalize">{type} Categories</h4>
                  {breakdown.categories.map((allocation, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <span className="font-medium">{allocation.category_name}</span>
                      <div className="text-right">
                        <div className="font-bold">{formatCurrency(allocation.allocated_amount)}</div>
                        <div className="text-xs text-gray-500">{allocation.percentage_of_income.toFixed(1)}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        );

      default:
        const envelopeResult = calculationResult as EnvelopeCalculationResult;
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="p-3 bg-purple-50 rounded">
                <div className="font-medium text-purple-900">Total Income</div>
                <div className="text-lg font-bold text-purple-600">{formatCurrency(envelopeResult.total_income)}</div>
              </div>
              <div className="p-3 bg-green-50 rounded">
                <div className="font-medium text-green-900">Total Allocated</div>
                <div className="text-lg font-bold text-green-600">{formatCurrency(envelopeResult.total_allocated)}</div>
              </div>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">Envelope Allocations</h4>
              {envelopeResult.envelopes.map((envelope, index) => (
                <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <div>
                    <span className="font-medium">{envelope.category_name}</span>
                    <Badge variant="outline" className="ml-2 text-xs">{envelope.priority}</Badge>
                  </div>
                  <div className="text-right">
                    <div className="font-bold">{formatCurrency(envelope.envelope_amount)}</div>
                    <div className="text-xs text-gray-500">{envelope.percentage_of_income.toFixed(1)}%</div>
                  </div>
                </div>
              ))}
            </div>

            {envelopeResult.unallocated !== 0 && (
              <div className={`p-3 border rounded ${envelopeResult.unallocated > 0 ? 'bg-yellow-50 border-yellow-200' : 'bg-red-50 border-red-200'}`}>
                <div className={`font-medium ${envelopeResult.unallocated > 0 ? 'text-yellow-800' : 'text-red-800'}`}>
                  {envelopeResult.unallocated > 0 ? 'Unallocated' : 'Over-allocated'}: {formatCurrency(Math.abs(envelopeResult.unallocated))}
                </div>
              </div>
            )}
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="lg:ml-64 p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-64 bg-gray-200 rounded"></div>
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
          <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <div className="text-red-500 text-xl mb-4">{error}</div>
          <Button onClick={loadMethodologyData} className="btn-primary">
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="lg:ml-64 p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Budget Methodologies</h1>
          <p className="text-gray-600">Choose and configure your budgeting approach</p>
        </div>
        <div className="flex space-x-2 mt-4 sm:mt-0">
          <Button onClick={handleCompareMethodologies} variant="outline" className="btn-secondary">
            <BarChart3 className="w-4 h-4 mr-2" />
            Compare
          </Button>
          <Button onClick={loadMethodologyData} variant="outline" className="btn-primary">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Current Active Methodology */}
      {activeMethodology && (
        <div className="card mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Active Methodology</h2>
            <Badge variant="default" className="bg-green-100 text-green-800">
              <CheckCircle className="w-3 h-3 mr-1" />
              Active
            </Badge>
          </div>

          <div className="flex items-start space-x-4">
            <div className={`p-3 rounded-full ${getMethodologyColor(activeMethodology.methodology_type)}`}>
              {getMethodologyIcon(activeMethodology.methodology_type)}
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-1">{activeMethodology.name}</h3>
              <p className="text-gray-600 text-sm mb-3">{activeMethodology.description}</p>
              <div className="flex space-x-2">
                <Button
                  onClick={() => handleCalculateMethodology(activeMethodology)}
                  disabled={calculationLoading}
                  className="btn-primary"
                  size="sm"
                >
                  <Calculator className="w-4 h-4 mr-2" />
                  {calculationLoading ? 'Calculating...' : 'Calculate Budget'}
                </Button>
                <Button
                  onClick={() => setSelectedMethodology(activeMethodology)}
                  variant="outline"
                  size="sm"
                >
                  <Settings className="w-4 h-4 mr-2" />
                  Configure
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Methodology Tabs */}
      <div className="card">
        <Tabs defaultValue="available" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="available">Available Methodologies</TabsTrigger>
            <TabsTrigger value="recommendations">AI Recommendations</TabsTrigger>
            <TabsTrigger value="comparison">Comparison</TabsTrigger>
          </TabsList>

          <TabsContent value="available" className="mt-6">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Choose Your Budgeting Method</h3>
                <p className="text-gray-600">Select the budgeting methodology that best fits your financial goals and lifestyle.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {methodologies.map((methodology) => (
                  <div
                    key={methodology.id}
                    className={`p-6 border rounded-lg hover:shadow-md transition-shadow ${
                      methodology.is_active ? 'border-green-200 bg-green-50' : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className={`p-2 rounded-full ${getMethodologyColor(methodology.methodology_type)}`}>
                        {getMethodologyIcon(methodology.methodology_type)}
                      </div>
                      {methodology.is_active && (
                        <Badge variant="default" className="bg-green-100 text-green-800 text-xs">
                          Active
                        </Badge>
                      )}
                    </div>

                    <h4 className="font-semibold text-gray-900 mb-2">{methodology.name}</h4>
                    <p className="text-gray-600 text-sm mb-4 line-clamp-3">{methodology.description}</p>

                    <div className="flex space-x-2">
                      {!methodology.is_active && (
                        <Button
                          onClick={() => handleActivateMethodology(methodology)}
                          size="sm"
                          className="btn-primary flex-1"
                        >
                          <Play className="w-3 h-3 mr-1" />
                          Activate
                        </Button>
                      )}
                      <Button
                        onClick={() => handleCalculateMethodology(methodology)}
                        disabled={calculationLoading}
                        variant="outline"
                        size="sm"
                        className="flex-1"
                      >
                        <Calculator className="w-3 h-3 mr-1" />
                        Preview
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="recommendations" className="mt-6">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Personalized Recommendations</h3>
                <p className="text-gray-600">Based on your spending patterns and financial profile</p>
              </div>

              {userProfile && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <div className="text-xl font-bold text-gray-900">{formatCurrency(userProfile.total_income)}</div>
                    <div className="text-sm text-gray-600">Monthly Income</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-gray-900">{userProfile.savings_rate.toFixed(1)}%</div>
                    <div className="text-sm text-gray-600">Savings Rate</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-gray-900">{userProfile.categories_count}</div>
                    <div className="text-sm text-gray-600">Categories</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-red-600">{userProfile.overspending_categories}</div>
                    <div className="text-sm text-gray-600">Over Budget</div>
                  </div>
                </div>
              )}

              <div className="space-y-4">
                {recommendations.length === 0 ? (
                  <div className="text-center py-8">
                    <Lightbulb className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">No recommendations available. Add some transactions to get personalized suggestions.</p>
                  </div>
                ) : (
                  recommendations.map((recommendation, index) => (
                    <div key={index} className="p-6 border border-blue-200 bg-blue-50 rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            {getMethodologyIcon(recommendation.methodology_type)}
                            <h4 className="font-semibold text-blue-900 capitalize">
                              {recommendation.methodology_type.replace('_', ' ')} Budgeting
                            </h4>
                            <Badge variant="outline" className="bg-blue-100 text-blue-800">
                              {recommendation.confidence}% match
                            </Badge>
                          </div>
                          <p className="text-blue-800 mb-2">{recommendation.reason}</p>
                          <p className="text-sm text-blue-600">{recommendation.best_for}</p>
                        </div>
                        <Button
                          onClick={() => {
                            const methodology = methodologies.find(m => m.methodology_type === recommendation.methodology_type);
                            if (methodology) handleActivateMethodology(methodology);
                          }}
                          size="sm"
                          className="ml-4"
                        >
                          Use This
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="comparison" className="mt-6">
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Methodology Comparison</h3>
                  <p className="text-gray-600">Compare different budgeting approaches side-by-side</p>
                </div>
                <div className="flex items-center space-x-2">
                  <Input
                    type="number"
                    placeholder="Total Income"
                    value={totalIncome || ''}
                    onChange={(e) => setTotalIncome(parseFloat(e.target.value) || 0)}
                    className="w-32"
                  />
                  <Button onClick={handleCompareMethodologies} className="btn-primary">
                    Compare
                  </Button>
                </div>
              </div>

              {comparisons.length === 0 ? (
                <div className="text-center py-8">
                  <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Click "Compare" to see different methodologies side-by-side</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {comparisons.map((comparison, index) => (
                    <div key={index} className="p-6 border rounded-lg">
                      <div className="flex items-center space-x-2 mb-4">
                        <div className={`p-2 rounded-full ${getMethodologyColor(comparison.methodology_type)}`}>
                          {getMethodologyIcon(comparison.methodology_type)}
                        </div>
                        <h4 className="font-semibold text-gray-900">{comparison.methodology_name}</h4>
                        {comparison.methodology_id === activeMethodology?.id && (
                          <Badge variant="default" className="bg-green-100 text-green-800 text-xs">
                            Current
                          </Badge>
                        )}
                      </div>
                      <div className="text-sm space-y-2">
                        {renderCalculationResult()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Calculation Results Dialog */}
      <Dialog open={isCalculationDialogOpen} onOpenChange={setIsCalculationDialogOpen}>
        <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Budget Calculation Results</DialogTitle>
            <DialogDescription>
              Preview your budget allocation using the selected methodology
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            {renderCalculationResult()}

            {calculationResult?.recommendations && calculationResult.recommendations.length > 0 && (
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded">
                <h5 className="font-medium text-yellow-900 mb-2">Recommendations:</h5>
                <ul className="text-sm text-yellow-800 space-y-1">
                  {calculationResult.recommendations.map((rec, index) => (
                    <li key={index}>• {rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCalculationDialogOpen(false)}>
              Cancel
            </Button>
            <Button 
              onClick={() => selectedMethodology && handleApplyMethodology(selectedMethodology, true)}
              disabled={calculationLoading}
              className="btn-primary"
            >
              {calculationLoading ? 'Applying...' : 'Apply to Budget'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default BudgetMethodologyPage;
