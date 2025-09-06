import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    this.setupInterceptors();
  }
  
  private setupInterceptors() {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const refreshToken = localStorage.getItem('refreshToken');
            if (refreshToken) {
              const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
                headers: { Authorization: `Bearer ${refreshToken}` }
              });
              
              const { access_token } = response.data;
              localStorage.setItem('authToken', access_token);
              
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, redirect to login
            localStorage.removeItem('authToken');
            localStorage.removeItem('refreshToken');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );
  }
  
  // Market Data APIs
  async getSymbols(exchange?: string) {
    return this.client.get('/api/v1/market/symbols', { params: { exchange } });
  }
  
  async getOHLC(symbol: string, timeframe: string = '1d', limit: number = 100) {
    return this.client.get(`/api/v1/market/ohlc/${symbol}`, {
      params: { timeframe, limit }
    });
  }
  
  async getQuote(symbol: string) {
    return this.client.get(`/api/v1/market/quote/${symbol}`);
  }
  
  // Authentication APIs
  async login(username: string, password: string) {
    return this.client.post('/auth/login', { username, password });
  }
  
  async register(userData: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
  }) {
    return this.client.post('/auth/register', userData);
  }
  
  async getCurrentUser() {
    return this.client.get('/auth/me');
  }
  
  // Trading APIs
  async placeOrder(orderData: {
    symbol: string;
    exchange: string;
    side: string;
    quantity: number;
    order_type: string;
    price?: number;
  }) {
    return this.client.post('/api/v1/execution/orders', orderData);
  }
  
  async getOrders() {
    return this.client.get('/api/v1/execution/orders');
  }
  
  async cancelOrder(orderId: string) {
    return this.client.delete(`/api/v1/execution/orders/${orderId}`);
  }
  
  async getPositions() {
    return this.client.get('/api/v1/portfolio/positions');
  }
  
  // Portfolio APIs
  async getPortfolio() {
    return this.client.get('/api/v1/portfolio');
  }
  
  async getPortfolioHistory(days: number = 30) {
    return this.client.get('/api/v1/portfolio/history', { params: { days } });
  }
  
  // Broker APIs
  async getBrokerAccounts() {
    return this.client.get('/api/v1/brokers/accounts');
  }
  
  async addBrokerAccount(brokerData: {
    broker_name: string;
    account_id: string;
    api_key: string;
    api_secret: string;
  }) {
    return this.client.post('/api/v1/brokers/accounts', brokerData);
  }
  
  // Generic methods
  async get(url: string, params?: any) {
    return this.client.get(url, { params });
  }
  
  async post(url: string, data?: any) {
    return this.client.post(url, data);
  }
  
  async put(url: string, data?: any) {
    return this.client.put(url, data);
  }
  
  async delete(url: string) {
    return this.client.delete(url);
  }
}

export const api = new ApiClient();
export default api;
