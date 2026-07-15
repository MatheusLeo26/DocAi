function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

/**
 * Wrapper around fetch that automatically handles expired sessions.
 * Se o cookie expirar e a API retornar 401, redireciona para login.
 */
async function authFetch(url, options = {}) {
    options.headers = options.headers || {};
    
    // Add Authorization header if token exists in localStorage
    const token = localStorage.getItem('token');
    if (token) {
        if (options.headers instanceof Headers) {
            options.headers.set('Authorization', `Bearer ${token}`);
        } else {
            options.headers['Authorization'] = `Bearer ${token}`;
        }
    }

    // Add X-CSRF-TOKEN header for CSRF protection
    const csrfToken = getCookie('csrf_access_token');
    if (csrfToken) {
        if (options.headers instanceof Headers) {
            options.headers.set('X-CSRF-TOKEN', csrfToken);
        } else {
            options.headers['X-CSRF-TOKEN'] = csrfToken;
        }
    }

    const res = await fetch(url, options);

    if (res.status === 401) {
        alert('Sua sessão expirou. Faça login novamente.');
        localStorage.removeItem('token');
        window.location.href = '/login';
        return null;
    }

    return res;
}

