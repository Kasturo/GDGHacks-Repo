/**
 * Backend base URL. Set VITE_API_URL in `.env` at repo root OR in src/frontend
 * (no trailing slash). Falls back so dev works without any env file.
 */
const raw = import.meta.env.VITE_API_URL;
export const apiBaseUrl =
  typeof raw === 'string' && raw.trim() !== '' ? raw.replace(/\/+$/, '') : 'http://127.0.0.1:8000';
