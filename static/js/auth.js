/**
 * Wrapper around fetch that automatically handles expired sessions.
 * Se o cookie expirar e a API retornar 401, redireciona para login.
 */
async function authFetch(url, options = {}) {
    // Como estamos usando HttpOnly Cookies, o navegador os envia automaticamente
    // (mesma origem). Apenas enviamos a requisição normal.
    const res = await fetch(url, options);

    if (res.status === 401) {
        alert('Sua sessão expirou. Faça login novamente.');
        localStorage.removeItem('token');
        window.location.href = '/login';
        return null;
    }

    return res;
}
