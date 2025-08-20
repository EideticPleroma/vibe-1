import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Settings,
  Target,
  DollarSign,
  BarChart3,
  Copy,
  RefreshCw
} from 'lucide-react';

// Import UI components
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';

import {
  Category,
  BudgetProgress,
  BudgetSummary,
  BudgetSuggestion,
  BudgetFormData,
  EffectiveBudgetCalculation,
} from '../types';
import {
  categoriesApi,
  budgetApi,
  formatCurrency,
  handleApiError,
} from '../services/api';

const Budget: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [budgetProgress, setBudgetProgress] = useState<BudgetProgress[]>([]);
  const [budgetSummary, setBudgetSummary] = useState<BudgetSummary | null>(null);
  const [suggestions, setSuggestions] = useState<BudgetSuggestion[]>([]);
  const [effectiveBudgets, setEffectiveBudgets] = useState<EffectiveBudgetCalculation[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [budgetForm, setBudgetForm] = useState<BudgetFormData>({
    category_id: 0,
    budget_limit: 0,
    budget_period: 'monthly',
    budget_type: 'fixed',
    budget_priority: 'essential',
    budget_percentage: undefined,
    budget_rolling_months: 3,
  });

  useEffect(() => {
    loadBudgetData();
  }, []);

  const loadBudgetData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [categoriesData, progressData, suggestionsData, effectiveData] = await Promise.all([
        categoriesApi.getAll(),
        budgetApi.getProgress(),
        budgetApi.getSuggestions(),
        budgetApi.calculateEffectiveBudget(),
      ]);

      const expenseCategories = categoriesData.filter(cat => cat.type === 'expense');
      setCategories(expenseCategories);
      setBudgetProgress(progressData.progress);
      setBudgetSummary(progressData.summary);
      setSuggestions(suggestionsData.suggestions);
      setEffectiveBudgets(effectiveData.calculations);
    } catch (err) {
      setError(handleApiError(err as any));
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'under': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'over': return 'text-orange-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'under': return <CheckCircle className="w-4 h-4" />;
      case 'warning': return <AlertTriangle className="w-4 h-4" />;
      case 'over':
      case 'critical': return <AlertTriangle className="w-4 h-4" />;
      default: return <Target className="w-4 h-4" />;
    }
  };



  const handleBudgetSubmit = async () => {
    if (!selectedCategory) return;

    try {
      await budgetApi.updateCategoryBudget(selectedCategory.id, budgetForm);
      await loadBudgetData();
      setIsDialogOpen(false);
      setSelectedCategory(null);
    } catch (err) {
      setError(handleApiError(err as any));
    }
  };

  const openBudgetDialog = (category: Category) => {
    setSelectedCategory(category);
    setBudgetForm({
      category_id: category.id,
      budget_limit: category.budget_limit || 0,
      budget_period: category.budget_period || 'monthly',
      budget_type: category.budget_type || 'fixed',
      budget_priority: category.budget_priority || 'essential',
      budget_percentage: category.budget_percentage,
      budget_rolling_months: category.budget_rolling_months || 3,
    });
    setIsDialogOpen(true);
  };

  const copyBudgetTemplate = async () => {
    try {
      await budgetApi.copyBudgetTemplate({ inflation_adjustment: 3 });
      await loadBudgetData();
    } catch (err) {
      setError(handleApiError(err as any));
    }
  };

  if (loading) {
    return (
      <div className="lg:ml-64 p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
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

  return (
    <div className="lg:ml-64 p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Budget Tracker</h1>
          <p className="text-gray-600">Monitor and manage your spending budgets</p>
        </div>
        <div className="flex space-x-2 mt-4 sm:mt-0">
          <Button onClick={copyBudgetTemplate} variant="outline" className="btn-secondary">
            <Copy className="w-4 h-4 mr-2" />
            Copy Template
          </Button>
          <Button onClick={loadBudgetData} variant="outline" className="btn-primary">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Budget Summary Cards */}
      {budgetSummary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Budgeted */}
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Budgeted</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(budgetSummary.total_budgeted)}
                </p>
              </div>
              <div className="p-3 bg-primary-100 rounded-full">
                <DollarSign className="h-6 w-6 text-primary-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-gray-600 font-medium">
                {budgetSummary.categories_count} categories
              </span>
            </div>
          </div>

          {/* Total Spent */}
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Spent</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(budgetSummary.total_spent)}
                </p>
              </div>
              <div className="p-3 bg-warning-100 rounded-full">
                <BarChart3 className="h-6 w-6 text-warning-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-warning-600 font-medium">
                {Math.round(budgetSummary.overall_progress)}% of budget
              </span>
            </div>
          </div>

          {/* Remaining */}
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Remaining</p>
                <p className={`text-2xl font-bold ${
                  budgetSummary.total_remaining >= 0 ? 'text-success-600' : 'text-danger-600'
                }`}>
                  {formatCurrency(budgetSummary.total_remaining)}
                </p>
              </div>
              <div className="p-3 bg-success-100 rounded-full">
                <Target className="h-6 w-6 text-success-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className={`font-medium ${
                budgetSummary.total_remaining >= 0 ? 'text-success-600' : 'text-danger-600'
              }`}>
                {budgetSummary.total_remaining >= 0 ? 'Available' : 'Overspent'}
              </span>
            </div>
          </div>

          {/* Status */}
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Budget Status</p>
                <div className="flex items-center space-x-2 mt-1">
                  <Badge variant={budgetSummary.categories_over_budget > 0 ? "destructive" : "secondary"} className="text-xs">
                    {budgetSummary.categories_over_budget} over
                  </Badge>
                  <Badge variant={budgetSummary.categories_warning > 0 ? "secondary" : "outline"} className="text-xs">
                    {budgetSummary.categories_warning} warning
                  </Badge>
                </div>
              </div>
              <div className="p-3 bg-info-100 rounded-full">
                <TrendingUp className="h-6 w-6 text-info-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-gray-600 font-medium">
                {budgetSummary.categories_under_budget} under budget
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Budget Tabs */}
      <div className="card">
        <Tabs defaultValue="progress" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="progress">Budget Progress</TabsTrigger>
            <TabsTrigger value="suggestions">AI Suggestions</TabsTrigger>
            <TabsTrigger value="effective">Effective Budgets</TabsTrigger>
            <TabsTrigger value="settings">Budget Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="progress" className="mt-6">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Budget Progress</h3>
                <p className="text-gray-600">Real-time progress for all expense categories</p>
              </div>

              <div className="space-y-4">
                {budgetProgress.map((progress) => (
                  <div key={progress.category_id} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-900">{progress.category_name}</span>
                        <Badge variant="outline" className={`${getStatusColor(progress.status)} border-0`}>
                          {getStatusIcon(progress.status)}
                          <span className="ml-1 capitalize">{progress.status}</span>
                        </Badge>
                      </div>
                      <div className="text-right">
                        <div className="font-medium text-gray-900">
                          {formatCurrency(progress.spent_amount)} / {formatCurrency(progress.budget_limit)}
                        </div>
                        <div className="text-sm text-gray-500">
                          {formatCurrency(progress.remaining_amount)} remaining
                        </div>
                      </div>
                    </div>
                    <div className="mb-2">
                      <Progress
                        value={Math.min(progress.spent_percentage, 100)}
                        className="h-2"
                      />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>{Math.round(progress.spent_percentage)}% spent</span>
                      <span>{progress.days_remaining} days remaining</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="suggestions" className="mt-6">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Budget Suggestions</h3>
                <p className="text-gray-600">Smart recommendations based on your spending patterns</p>
              </div>

              {suggestions.length === 0 ? (
                <div className="text-center py-8">
                  <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No suggestions available. Add some transactions to get personalized recommendations.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {suggestions.map((suggestion, index) => (
                    <div key={index} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">{suggestion.category_name}</h4>
                          <p className="text-sm text-gray-600 mt-1">{suggestion.reasoning}</p>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-lg text-primary-600">
                            {formatCurrency(suggestion.suggested_amount)}
                          </div>
                          <div className="text-xs text-gray-500">
                            {Math.round(suggestion.confidence_score * 100)}% confidence
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="effective" className="mt-6">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Effective Budget Calculations</h3>
                <p className="text-gray-600">Calculated budgets based on your income and spending patterns</p>
              </div>

              <div className="space-y-4">
                {effectiveBudgets.map((calc) => (
                  <div key={calc.category_id} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-center">
                      <div>
                        <h4 className="font-medium text-gray-900">{calc.category_name}</h4>
                        <p className="text-sm text-gray-600">{calc.calculation_method}</p>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-lg text-primary-600">
                          {formatCurrency(calc.effective_budget)}
                        </div>
                        {calc.factors.total_income && (
                          <div className="text-xs text-gray-500">
                            Based on {formatCurrency(calc.factors.total_income)} income
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="settings" className="mt-6">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Budget Settings</h3>
                <p className="text-gray-600">Configure budgets for expense categories</p>
              </div>

              <div className="space-y-4">
                {categories.map((category) => (
                  <div key={category.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-medium text-gray-900">{category.name}</h4>
                      <p className="text-sm text-gray-600">
                        Current: {category.budget_limit ? formatCurrency(category.budget_limit) : 'No budget set'}
                      </p>
                    </div>
                    <Button
                      onClick={() => openBudgetDialog(category)}
                      variant="outline"
                      size="sm"
                      className="btn-secondary"
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      Configure
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Budget Configuration Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Configure Budget</DialogTitle>
            <DialogDescription>
              Set up budget parameters for {selectedCategory?.name}
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="budget_limit">Budget Limit</Label>
              <Input
                id="budget_limit"
                type="number"
                value={budgetForm.budget_limit}
                onChange={(e) => setBudgetForm({ ...budgetForm, budget_limit: parseFloat(e.target.value) || 0 })}
                placeholder="0.00"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="budget_period">Period</Label>
              <Select
                value={budgetForm.budget_period}
                onValueChange={(value: any) => setBudgetForm({ ...budgetForm, budget_period: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="daily">Daily</SelectItem>
                  <SelectItem value="weekly">Weekly</SelectItem>
                  <SelectItem value="monthly">Monthly</SelectItem>
                  <SelectItem value="yearly">Yearly</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="budget_type">Type</Label>
              <Select
                value={budgetForm.budget_type}
                onValueChange={(value: any) => setBudgetForm({ ...budgetForm, budget_type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fixed">Fixed Amount</SelectItem>
                  <SelectItem value="percentage">Percentage of Income</SelectItem>
                  <SelectItem value="rolling_average">Rolling Average</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="budget_priority">Priority</Label>
              <Select
                value={budgetForm.budget_priority}
                onValueChange={(value: any) => setBudgetForm({ ...budgetForm, budget_priority: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="essential">Essential</SelectItem>
                  <SelectItem value="important">Important</SelectItem>
                  <SelectItem value="discretionary">Discretionary</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {budgetForm.budget_type === 'percentage' && (
              <div className="space-y-2">
                <Label htmlFor="budget_percentage">Percentage</Label>
                <Input
                  id="budget_percentage"
                  type="number"
                  value={budgetForm.budget_percentage || ''}
                  onChange={(e) => setBudgetForm({ ...budgetForm, budget_percentage: parseFloat(e.target.value) || undefined })}
                  placeholder="10"
                />
              </div>
            )}

            {budgetForm.budget_type === 'rolling_average' && (
              <div className="space-y-2">
                <Label htmlFor="budget_rolling_months">Months</Label>
                <Input
                  id="budget_rolling_months"
                  type="number"
                  value={budgetForm.budget_rolling_months}
                  onChange={(e) => setBudgetForm({ ...budgetForm, budget_rolling_months: parseInt(e.target.value) || 3 })}
                  placeholder="3"
                />
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)} className="btn-secondary">
              Cancel
            </Button>
            <Button onClick={handleBudgetSubmit} className="btn-primary">Save Budget</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Budget;
