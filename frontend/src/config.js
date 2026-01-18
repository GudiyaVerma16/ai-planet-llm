// API Configuration
// Get API base URL from environment variable, with fallback
const envApiUrl = import.meta.env.VITE_API_BASE_URL
export const API_BASE_URL = (envApiUrl && envApiUrl.trim() !== '') 
  ? envApiUrl.trim() 
  : 'http://localhost:8001/api'
