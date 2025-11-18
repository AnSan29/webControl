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

// Paletas curadas por modelo (colores tomados del manual PDF)
const BUSINESS_PALETTES = {
    artesanias: [
        { id: 'artesanias-arcilla', label: 'Arcilla dorada', primary: '#CBB67C', secondary: '#8B5E3C', accent: '#FAF4ED', background: '#FBF7F0' },
        { id: 'artesanias-olivo', label: 'Textiles oliva', primary: '#808000', secondary: '#7E8D60', accent: '#D2D48C', background: '#FFF5E1' },
        { id: 'artesanias-terracota', label: 'Terracota viva', primary: '#A0522D', secondary: '#E1A95F', accent: '#D8B4A0', background: '#F1E4C6' },
        { id: 'artesanias-bosque', label: 'Bosque cálido', primary: '#4B2E05', secondary: '#D2D48C', accent: '#A9BA9D', background: '#FBF7F0' }
    ],
    cocina: [
        { id: 'cocina-coral', label: 'Gourmet coral', primary: '#E63956', secondary: '#FF8C42', accent: '#FFD07F', background: '#FFF8E8' },
        { id: 'cocina-verde', label: 'Verde orgánico', primary: '#249D8F', secondary: '#5B8A72', accent: '#BFCBA8', background: '#F1FAEE' },
        { id: 'cocina-brasa', label: 'Brasa clásica', primary: '#9E2A2B', secondary: '#C85C5C', accent: '#6B4F4F', background: '#E3D7BF' },
        { id: 'cocina-caramelo', label: 'Caramelo suave', primary: '#F4A261', secondary: '#D9BF77', accent: '#EFD9B4', background: '#F1FAEE' }
    ],
    adecuaciones: [
        { id: 'adecuaciones-azul', label: 'Azul técnico', primary: '#264653', secondary: '#2A9D8F', accent: '#E9C464', background: '#F4A261' },
        { id: 'adecuaciones-industrial', label: 'Industrial nocturno', primary: '#003049', secondary: '#EAE2B7', accent: '#F4BA00', background: '#FAF4ED' },
        { id: 'adecuaciones-marina', label: 'Marina moderna', primary: '#1D3557', secondary: '#457B9D', accent: '#A8DADC', background: '#F1FAEE' },
        { id: 'adecuaciones-contraste', label: 'Contraste profesional', primary: '#003566', secondary: '#FFC300', accent: '#E5E5E5', background: '#1C1C1C' }
    ],
    belleza: [
        { id: 'belleza-rosa', label: 'Rosa empolvado', primary: '#E5989B', secondary: '#2E2E2E', accent: '#FFD6BA', background: '#F7F7F7' },
        { id: 'belleza-glow', label: 'Glow romántico', primary: '#EC407A', secondary: '#FFD6E0', accent: '#FCE4EC', background: '#FFF5E4' },
        { id: 'belleza-editorial', label: 'Editorial lila', primary: '#6A1B9A', secondary: '#BA68C8', accent: '#F3E5F5', background: '#F7F7F7' },
        { id: 'belleza-cherry', label: 'Cherry chic', primary: '#880E4F', secondary: '#F06292', accent: '#F8BBD0', background: '#FFD6BA' }
    ],
    chivos: [
        { id: 'chivos-campo', label: 'Campo musgo', primary: '#6B705C', secondary: '#A5A58D', accent: '#FFE8D6', background: '#CB997E' },
        { id: 'chivos-rustico', label: 'Rústico premium', primary: '#343A40', secondary: '#7C6A0A', accent: '#DAD2BC', background: '#B09E99' },
        { id: 'chivos-granja', label: 'Granja fresca', primary: '#283618', secondary: '#606C38', accent: '#FEFAE0', background: '#DDA15E' },
        { id: 'chivos-tierra', label: 'Tierra suave', primary: '#C2B280', secondary: '#7D7461', accent: '#EAE0CC', background: '#A68A64' }
    ]
};

function getPalettesForModel(modelId) {
    return BUSINESS_PALETTES[modelId] || [];
}

function findPaletteForModel(modelId, paletteId) {
    return (BUSINESS_PALETTES[modelId] || []).find(palette => palette.id === paletteId);
}

// Exponer helpers para scripts inline
window.BUSINESS_PALETTES = BUSINESS_PALETTES;
window.getPalettesForModel = getPalettesForModel;
window.findPaletteForModel = findPaletteForModel;
