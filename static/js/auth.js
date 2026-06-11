/**
 * Wrapper around fetch that automatically handles expired JWT tokens.
 * If a 401 is received, clears the token and redirects to login.
 */
async function authFetch(url, options = {}) {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    if (!options.headers) {
        options.headers = {};
    }
    options.headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(url, options);

    if (res.status === 401) {
        localStorage.removeItem('token');
        alert('Sua sessão expirou. Faça login novamente.');
        window.location.href = '/login';
        return null;
    }

    return res;
}
