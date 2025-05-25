// API Configuration for AudioBrew
export const API_CONFIG = {
  // Use Render backend in production, local in development
  baseUrl: import.meta.env.PROD 
    ? 'https://audiobrew-backend.onrender.com'  // Your actual Render URL
    : 'http://localhost:8000',
  timeout: 30000,
  
  // Helper method to build API URLs
  url: (endpoint: string) => {
    // Remove leading slash if present to avoid double slashes
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    return `${API_CONFIG.baseUrl}/${cleanEndpoint}`;
  }
};

// Environment info for debugging
export const ENV_INFO = {
  isProd: import.meta.env.PROD,
  isDev: import.meta.env.DEV,
  mode: import.meta.env.MODE,
  apiBase: API_CONFIG.baseUrl
}; 