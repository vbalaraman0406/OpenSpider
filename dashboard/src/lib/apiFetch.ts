/**
 * Authenticated fetch utility for OpenSpider Dashboard.
 * Attaches the VITE_API_KEY to every API request via X-API-Key header.
 */

const API_KEY = import.meta.env.VITE_API_KEY || '';

export const apiFetch = (url: string, options: RequestInit = {}): Promise<Response> => {
    const headers = new Headers(options.headers || {});
    headers.set('X-API-Key', API_KEY);
    return fetch(url, { ...options, headers });
};

export const getApiKey = (): string => API_KEY;
