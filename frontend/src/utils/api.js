const API_URL = process.env.REACT_APP_BACKEND_URL;

export async function apiCall(path, options = {}, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(`${API_URL}${path}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || res.statusText);
      }
      return res;
    } catch (err) {
      if (i === retries - 1) throw err;
      await new Promise(r => setTimeout(r, Math.pow(2, i) * 1000));
    }
  }
}

export function getAdminToken() {
  return localStorage.getItem('admin_token');
}

export async function adminApiCall(path, options = {}) {
  const token = getAdminToken();
  if (!token) throw new Error('Not authenticated');
  return apiCall(path, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    },
  }, 1);
}
