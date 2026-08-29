// Configuration for backend API URL
// In local development (npm run dev), defaults to http://127.0.0.1:5000
// In production (Vercel build), defaults to live PythonAnywhere API if VITE_API_URL is unset
export const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://127.0.0.1:5000' : 'https://sehaj1104.pythonanywhere.com');

