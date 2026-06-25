// Configuration for backend API URL
// In development, it defaults to the local Flask server (http://127.0.0.1:5000)
// In production, Vite will use the VITE_API_URL environment variable from the hosting service (e.g. Vercel)
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';
