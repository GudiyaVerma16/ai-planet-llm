// API Configuration
// Get API base URL from environment variable, with fallback
const envApiUrl = import.meta.env.VITE_API_BASE_URL

// Try to auto-detect backend URL on Render
const getApiBaseUrl = () => {
  // If environment variable is set, use it
  if (envApiUrl && envApiUrl.trim() !== '') {
    return envApiUrl.trim()
  }
  
  // If we're on Render (onrender.com domain), try to construct backend URL
  if (typeof window !== 'undefined' && window.location.hostname.includes('onrender.com')) {
    const currentHost = window.location.hostname
    // Try common backend naming patterns
    const backendHost = currentHost
      .replace('frontend', 'backend')
      .replace('ai-planet-llm', 'ai-planet-backend')
      .replace('ai-planet-llm-1', 'ai-planet-backend')
    
    // If hostname changed, construct backend URL
    if (backendHost !== currentHost) {
      return `https://${backendHost}/api`
    }
    
    // If same hostname, try adding -backend suffix
    if (!currentHost.includes('backend')) {
      const parts = currentHost.split('.')
      if (parts.length > 0) {
        parts[0] = parts[0] + '-backend'
        return `https://${parts.join('.')}/api`
      }
    }
  }
  
  // Default fallback for local development
  return 'http://localhost:8001/api'
}

export const API_BASE_URL = getApiBaseUrl()

// Debug log (only in development)
if (import.meta.env.DEV) {
  console.log('API_BASE_URL:', API_BASE_URL)
  console.log('VITE_API_BASE_URL env:', envApiUrl)
}
