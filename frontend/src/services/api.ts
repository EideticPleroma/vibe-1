// API service for Personal Finance App
// Handles all HTTP requests to the Flask backend

import axios, { AxiosResponse } from 'axios';
import {
  Category,
  Transaction,
  Investment,
  DashboardData,
  SpendingTrends,
  InvestmentPerformance,
  TransactionsResponse,
  TransactionFormData,
  CategoryFormData,
  InvestmentFormData,
  ApiError
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.data?.error) {
      console.error('API Error:', error.response.data.error);
    } else {
      console.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Categories API
export const categoriesApi = {
  getAll: async (): Promise<Category[]> => {
    const response = await api.get<Category[]>('/categories');
    return response.data;
  },

  create: async (data: CategoryFormData): Promise<Category> => {
    const response = await api.post<Category>('/categories', data);
    return response.data;
  },

  update: async (id: number, data: Partial<CategoryFormData>): Promise<Category> => {
    const response = await api.put<Category>(`/categories/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/categories/${id}`);
    return response.data;
  },
};

// Transactions API
export const transactionsApi = {
  getAll: async (params?: {
    page?: number;
    per_page?: number;
    category_id?: number;
    type?: 'income' | 'expense';
    start_date?: string;
    end_date?: string;
  }): Promise<TransactionsResponse> => {
    const response = await api.get<TransactionsResponse>('/transactions', { params });
    return response.data;
  },

  create: async (data: TransactionFormData): Promise<Transaction> => {
    const response = await api.post<Transaction>('/transactions', data);
    return response.data;
  },

  update: async (id: number, data: Partial<TransactionFormData>): Promise<Transaction> => {
    const response = await api.put<Transaction>(`/transactions/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/transactions/${id}`);
    return response.data;
  },
};

// Investments API
export const investmentsApi = {
  getAll: async (): Promise<Investment[]> => {
    const response = await api.get<Investment[]>('/investments');
    return response.data;
  },

  create: async (data: InvestmentFormData): Promise<Investment> => {
    const response = await api.post<Investment>('/investments', data);
    return response.data;
  },

  update: async (id: number, data: Partial<InvestmentFormData>): Promise<Investment> => {
    const response = await api.put<Investment>(`/investments/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/investments/${id}`);
    return response.data;
  },
};

// Dashboard API
export const dashboardApi = {
  getData: async (params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<DashboardData> => {
    const response = await api.get<DashboardData>('/dashboard', { params });
    return response.data;
  },
};

// Analytics API
export const analyticsApi = {
  getSpendingTrends: async (months: number = 6): Promise<SpendingTrends> => {
    const response = await api.get<SpendingTrends>('/analytics/spending-trends', {
      params: { months }
    });
    return response.data;
  },

  getInvestmentPerformance: async (): Promise<InvestmentPerformance> => {
    const response = await api.get<InvestmentPerformance>('/analytics/investment-performance');
    return response.data;
  },
};

// Utility functions
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

export const formatPercentage = (value: number): string => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
};

export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const getCategoryColor = (category: Category | undefined): string => {
  return category?.color || '#6b7280';
};

export const isPositiveAmount = (amount: number): boolean => {
  return amount > 0;
};

export const getTransactionTypeColor = (type: 'income' | 'expense'): string => {
  return type === 'income' ? 'text-success-600' : 'text-danger-600';
};

export const getTransactionTypeIcon = (type: 'income' | 'expense'): string => {
  return type === 'income' ? '↑' : '↓';
};

// Error handling utilities
export const handleApiError = (error: any): string => {
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

export const isApiError = (error: any): error is ApiError => {
  return error && typeof error.error === 'string';
};

export default api;
