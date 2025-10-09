import axios from 'axios';

// Base API configuration
// In development, use proxy (empty baseURL), in production use full URL
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? (process.env.REACT_APP_API_URL || 'https://api.quantumcertify.tech')
  : ''; // Use proxy in development

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 120 seconds (2 minutes) timeout for AI analysis
  withCredentials: true, // Include cookies for authentication
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`Making ${config.method?.toUpperCase()} request to: ${config.baseURL}${config.url}`);
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    
    if (error.code === 'ECONNABORTED') {
      error.message = 'Request timeout. Please try again.';
    } else if (error.code === 'ERR_NETWORK') {
      error.message = 'Network error. Please check if the backend server is running.';
    } else if (error.response) {
      // Server responded with error status
      error.message = error.response.data?.detail || error.response.data?.message || error.message;
    }
    
    return Promise.reject(error);
  }
);

// API service functions
export const apiService = {
  // Health check
  checkHealth: () => apiClient.get('/health'),
  
  // Get API root
  getRoot: () => apiClient.get('/'),
  
  // Upload and analyze certificate
  uploadCertificate: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.post('/upload-certificate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 180000, // 3 minutes for AI-powered certificate analysis
    });
  },
  
  // Get PQC algorithms
  getPQCAlgorithms: () => apiClient.get('/algorithms/pqc'),
  
  // Get dashboard statistics
  getDashboardStatistics: () => apiClient.get('/dashboard/stats'),
};

export default apiService;