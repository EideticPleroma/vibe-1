import React, { useState, useEffect } from 'react';
import { goalsApi, categoriesApi } from '../services/api';
import { BudgetGoal, BudgetGoalFormData, Category } from '../types';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Progress } from '../components/ui/progress';
import { Card } from '../components/ui/card';

const GoalsPage: React.FC = () => {
  const [goals, setGoals] = useState<BudgetGoal[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [formData, setFormData] = useState<BudgetGoalFormData>({ name: '', target_amount: 0, deadline: '' });
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      await Promise.all([fetchGoals(), fetchCategories()]);
    } catch (err) {
      setError('Failed to load data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchGoals = async () => {
    try {
      const data = await goalsApi.getAll();
      setGoals(data);
    } catch (err) {
      console.error('Error fetching goals:', err);
      throw err;
    }
  };

  const fetchCategories = async () => {
    try {
      const data = await categoriesApi.getAll();
      setCategories(data.filter(cat => cat.type === 'income'));
    } catch (err) {
      console.error('Error fetching categories:', err);
      throw err;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await goalsApi.update(editingId, formData);
      } else {
        await goalsApi.create(formData);
      }
      await fetchGoals();
      resetForm();
    } catch (err) {
      setError('Failed to save goal');
      console.error('Error saving goal:', err);
    }
  };

  const handleEdit = (goal: BudgetGoal) => {
    setFormData({
      name: goal.name,
      target_amount: goal.target_amount,
      deadline: goal.deadline ? goal.deadline.split('T')[0] : ''
    });
    setEditingId(goal.id);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this goal?')) return;
    
    try {
      await goalsApi.delete(id);
      await fetchGoals();
    } catch (err) {
      setError('Failed to delete goal');
      console.error('Error deleting goal:', err);
    }
  };

  const handleAllocateCategory = async (goalId: number, categoryId: number) => {
    try {
      await goalsApi.allocateCategory(goalId, categoryId);
      await fetchGoals();
    } catch (err) {
      setError('Failed to allocate category');
      console.error('Error allocating category:', err);
    }
  };

  const handleRemoveCategory = async (goalId: number, categoryId: number) => {
    try {
      await goalsApi.removeCategory(goalId, categoryId);
      await fetchGoals();
    } catch (err) {
      setError('Failed to remove category');
      console.error('Error removing category:', err);
    }
  };

  const handleUpdateProgress = async (id: number) => {
    try {
      await goalsApi.updateProgress(id);
      await fetchGoals();
    } catch (err) {
      setError('Failed to update progress');
      console.error('Error updating progress:', err);
    }
  };

  const resetForm = () => {
    setFormData({ name: '', target_amount: 0, deadline: '' });
    setEditingId(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading goals...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Budget Goals</h1>
        <p className="text-gray-600">Set and track your financial goals</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">{error}</p>
        </div>
      )}
      
      {/* Goal Form */}
      <Card className="p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">
          {editingId ? 'Edit Goal' : 'Create New Goal'}
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Goal Name</Label>
              <Input 
                id="name" 
                value={formData.name} 
                onChange={(e) => setFormData({...formData, name: e.target.value})} 
                placeholder="e.g., Emergency Fund"
                required 
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="target_amount">Target Amount ($)</Label>
              <Input 
                id="target_amount" 
                type="number" 
                min="0"
                step="0.01"
                value={formData.target_amount} 
                onChange={(e) => setFormData({...formData, target_amount: parseFloat(e.target.value) || 0})} 
                placeholder="0.00"
                required 
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="deadline">Target Deadline (Optional)</Label>
              <Input 
                id="deadline" 
                type="date" 
                value={formData.deadline} 
                onChange={(e) => setFormData({...formData, deadline: e.target.value})} 
              />
            </div>
          </div>
          
          <div className="flex space-x-2">
            <Button type="submit">
              {editingId ? 'Update Goal' : 'Create Goal'}
            </Button>
            {editingId && (
              <Button type="button" variant="outline" onClick={resetForm}>
                Cancel
              </Button>
            )}
          </div>
        </form>
      </Card>
      
      {/* Goals List */}
      <div className="space-y-6">
        <h2 className="text-2xl font-semibold">Your Goals</h2>
        
        {goals.length === 0 ? (
          <Card className="p-8 text-center">
            <p className="text-gray-500 text-lg">No goals yet. Create your first financial goal above!</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {goals.map(goal => (
              <Card key={goal.id} className="p-6">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900">{goal.name}</h3>
                    {goal.description && (
                      <p className="text-gray-600 text-sm mt-1">{goal.description}</p>
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Progress</span>
                      <span className="font-medium">{goal.progress_percentage.toFixed(1)}%</span>
                    </div>
                    <Progress value={goal.progress_percentage} className="w-full" />
                    <div className="flex justify-between text-sm text-gray-600">
                      <span>${goal.current_amount.toLocaleString()}</span>
                      <span>${goal.target_amount.toLocaleString()}</span>
                    </div>
                  </div>
                  
                  {goal.deadline && (
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Deadline:</span> {new Date(goal.deadline).toLocaleDateString()}
                    </div>
                  )}
                  
                  {goal.categories && goal.categories.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Linked Categories:</h4>
                      <div className="flex flex-wrap gap-1">
                        {goal.categories.map(cat => (
                          <span 
                            key={cat.id}
                            className="inline-flex items-center px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full"
                          >
                            {cat.name}
                            <button
                              onClick={() => handleRemoveCategory(goal.id, cat.id)}
                              className="ml-1 text-blue-600 hover:text-blue-800"
                            >
                              ×
                            </button>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex space-x-2">
                    <Button size="sm" variant="outline" onClick={() => handleEdit(goal)}>
                      Edit
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => handleUpdateProgress(goal.id)}>
                      Update Progress
                    </Button>
                    <Button size="sm" variant="destructive" onClick={() => handleDelete(goal.id)}>
                      Delete
                    </Button>
                  </div>
                  
                  {categories.length > 0 && (
                    <div className="pt-2 border-t">
                      <Label className="text-sm font-medium">Link Category:</Label>
                      <div className="flex gap-2 mt-1">
                        <select 
                          className="flex-1 px-2 py-1 text-sm border rounded"
                          onChange={(e) => {
                            if (e.target.value) {
                              handleAllocateCategory(goal.id, parseInt(e.target.value));
                              e.target.value = '';
                            }
                          }}
                        >
                          <option value="">Select category...</option>
                          {categories
                            .filter(cat => !goal.categories?.some(gc => gc.id === cat.id))
                            .map(cat => (
                              <option key={cat.id} value={cat.id}>{cat.name}</option>
                            ))
                          }
                        </select>
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GoalsPage;