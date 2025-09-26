import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to: ${config.url}`);
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
    });
  },
  
  // Get public key algorithms (if implemented)
  getPublicKeyAlgorithms: () => apiClient.get('/public-key-algorithms'),
  
  // Get signature algorithms (if implemented)
  getSignatureAlgorithms: () => apiClient.get('/signature-algorithms'),
  
  // Get dashboard statistics
  getDashboardStatistics: () => apiClient.get('/dashboard-statistics'),
};

export default apiService;