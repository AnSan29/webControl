// API Base URL
const API_BASE = window.location.origin;

// Utilidad para obtener token
function getToken() {
    return localStorage.getItem('token');
}

// Utilidad para hacer peticiones autenticadas
async function fetchAPI(endpoint, options = {}) {
    const token = getToken();
    
    // Si el body es FormData, no agregar Content-Type (el navegador lo hace automáticamente)
    const isFormData = options.body instanceof FormData;
    
    const defaultOptions = {
        headers: {
            ...(!isFormData && { 'Content-Type': 'application/json' }),
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    });
    
    if (response.status === 401) {
        // Token inválido, redirigir a login
        localStorage.removeItem('token');
        window.location.href = '/';
        return;
    }
    
    return response;
}

// Verificar autenticación
async function checkAuth() {
    const token = getToken();
    
    if (!token) {
        window.location.href = '/';
        return false;
    }
    
    try {
        const response = await fetchAPI('/api/me');
        if (!response.ok) {
            localStorage.removeItem('token');
            window.location.href = '/';
            return false;
        }
        return true;
    } catch (error) {
        console.error('Error checking auth:', error);
        localStorage.removeItem('token');
        window.location.href = '/';
        return false;
    }
}

// Logout
function logout() {
    localStorage.removeItem('token');
    window.location.href = '/';
}

// Mostrar notificación
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Formatear fecha
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Formatear número
function formatNumber(num) {
    return new Intl.NumberFormat('es-ES').format(num);
}

// Copiar al portapapeles
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copiado al portapapeles', 'success');
    } catch (error) {
        console.error('Error copying to clipboard:', error);
        showNotification('Error al copiar', 'error');
    }
}

// Confirmar acción
function confirmAction(message) {
    return confirm(message);
}

// Cargar modelos de negocio
async function loadBusinessModels() {
    try {
        const response = await fetchAPI('/api/models');
        const data = await response.json();
        return data.models;
    } catch (error) {
        console.error('Error loading models:', error);
        return [];
    }
}

// Obtener icono de modelo
function getModelIcon(modelId) {
    const icons = {
        artesanias: '🎨',
        cocina: '🍳',
        adecuaciones: '🔧',
        belleza: '💇',
        chivos: '🐐'
    };
    return icons[modelId] || '📄';
}

// Obtener nombre de modelo
function getModelName(modelId) {
    const names = {
        artesanias: 'Artesanías',
        cocina: 'Cocina Doméstica',
        adecuaciones: 'Adecuaciones Menores',
        belleza: 'Belleza y Barbería',
        chivos: 'Cría de Chivos'
    };
    return names[modelId] || modelId;
}
