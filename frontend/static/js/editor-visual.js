const editorVisual = (() => {
    const state = {
        siteId: window.__SITE_ID__,
        siteState: {
            products: [],
            gallery_images: []
        },
        previewTimer: null,
        models: [],
        inputsBound: false,
        activePaletteId: null
    };

    const LOCAL_ASSET_HOSTS = new Set(['localhost', '127.0.0.1']);

    function canonicalizeAssetUrl(value) {
        if (!value || typeof value !== 'string') {
            return '';
        }
        let trimmed = value.trim();
        if (!trimmed) {
            return '';
        }
        if (/^data:/i.test(trimmed)) {
            return trimmed;
        }
        if (trimmed.startsWith('./')) {
            trimmed = trimmed.replace(/^\.\/+/, '');
        }
        if (trimmed.startsWith('images/')) {
            return trimmed;
        }
        if (trimmed.startsWith('/images/')) {
            return trimmed.replace(/^\/+/, '');
        }
        if (/^https?:\/\//i.test(trimmed) || trimmed.startsWith('//')) {
            try {
                const parsed = new URL(trimmed, window.location.origin);
                if (LOCAL_ASSET_HOSTS.has(parsed.hostname) && parsed.pathname.startsWith('/images/')) {
                    return parsed.pathname.replace(/^\/+/, '');
                }
            } catch (error) {
                return trimmed;
            }
            return trimmed;
        }
        return trimmed;
    }

    function canonicalizeGalleryList(items) {
        if (!Array.isArray(items)) {
            return [];
        }
        return items.map(item => canonicalizeAssetUrl(typeof item === 'string' ? item : ''));
    }

    function canonicalizeProductsList(items) {
        if (!Array.isArray(items)) {
            return [];
        }
        return items
            .filter(product => product && typeof product === 'object')
            .map(product => ({
                ...product,
                image: canonicalizeAssetUrl(product.image || '')
            }));
    }

    function canonicalizeSiteMedia() {
        state.siteState.logo_url = canonicalizeAssetUrl(state.siteState.logo_url || '');
        state.siteState.hero_image = canonicalizeAssetUrl(state.siteState.hero_image || '');
        state.siteState.about_image = canonicalizeAssetUrl(state.siteState.about_image || '');
        state.siteState.products = canonicalizeProductsList(state.siteState.products || []);
        state.siteState.gallery_images = canonicalizeGalleryList(state.siteState.gallery_images || []);
    }

    function normalizePaletteConfig(palette) {
        if (!palette) return null;
        return {
            id: palette.id,
            label: palette.label || 'Paleta',
            primary: palette.primary || palette.primary_color,
            secondary: palette.secondary || palette.secondary_color,
            accent: palette.accent || palette.tertiary || palette.accent_color,
            background: palette.background || palette.neutral || palette.background_color
        };
    }

    function renderPaletteSwatch(color, label) {
        if (!color) return '';
        const labels = {
            primary: 'Primario',
            secondary: 'Secundario',
            accent: 'Acento',
            background: 'Fondo'
        };
        const text = labels[label] || '';
        return `<span class="palette-swatch" style="background:${color}"><span>${text}</span></span>`;
    }

    function detectActivePalette(modelId) {
        if (typeof getPalettesForModel !== 'function' || !modelId) return null;
        const palettes = getPalettesForModel(modelId) || [];
        const primary = (state.siteState.primary_color || '').toLowerCase();
        const secondary = (state.siteState.secondary_color || '').toLowerCase();
        const match = palettes.find(palette => {
            const normalized = normalizePaletteConfig(palette);
            return normalized &&
                (normalized.primary || '').toLowerCase() === primary &&
                (normalized.secondary || '').toLowerCase() === secondary;
        });
        return match ? match.id : null;
    }

    function renderPaletteSuggestions(modelId = state.siteState.model_type) {
        const container = document.getElementById('paletteSuggestions');
        const helper = document.getElementById('paletteEmptyState');
        if (!container) return;

        if (typeof getPalettesForModel !== 'function' || !modelId) {
            container.innerHTML = '';
            if (helper) helper.textContent = 'Selecciona un modelo para ver sus paletas.';
            return;
        }

        const palettes = getPalettesForModel(modelId) || [];
        if (!palettes.length) {
            container.innerHTML = '';
            if (helper) helper.textContent = 'Este modelo no tiene paletas curadas, usa los selectores de color manualmente.';
            return;
        }

        if (helper) helper.textContent = '';

        container.innerHTML = palettes.map(palette => {
            const normalized = normalizePaletteConfig(palette);
            if (!normalized) return '';
            const isActive = state.activePaletteId === palette.id;
            return `
                <button type="button" class="palette-card ${isActive ? 'palette-card-active' : ''}" data-palette-id="${palette.id}">
                    <div class="flex items-center justify-between">
                        <span class="text-sm font-semibold ${isActive ? 'text-blue-600' : 'text-gray-800'}">${normalized.label}</span>
                        ${isActive ? '<span class="text-[10px] font-semibold text-blue-500 bg-blue-50 px-2 py-0.5 rounded-full">Aplicada</span>' : ''}
                    </div>
                    <div class="palette-swatches mt-3">
                        ${renderPaletteSwatch(normalized.primary, 'primary')}
                        ${renderPaletteSwatch(normalized.secondary, 'secondary')}
                        ${renderPaletteSwatch(normalized.accent, 'accent')}
                        ${renderPaletteSwatch(normalized.background, 'background')}
                    </div>
                    <p class="text-[11px] text-gray-500 mt-3 text-left">Haz clic para aplicar esta combinación en el editor.</p>
                </button>
            `;
        }).join('');

        container.querySelectorAll('[data-palette-id]').forEach(card => {
            card.addEventListener('click', () => {
                const paletteId = card.getAttribute('data-palette-id');
                const palette = palettes.find(item => item.id === paletteId);
                if (palette) {
                    applyPaletteSelection(palette);
                }
            });
        });
    }

    function applyPaletteSelection(palette) {
        const normalized = normalizePaletteConfig(palette);
        if (!normalized) return;
        state.activePaletteId = palette.id || null;
        if (normalized.primary) {
            state.siteState.primary_color = normalized.primary;
        }
        if (normalized.secondary) {
            state.siteState.secondary_color = normalized.secondary;
        }
        syncColorInputs();
        renderPaletteSuggestions();
        refreshPreview();
        showNotification(`Paleta "${normalized.label}" aplicada`, 'success');
    }

    function syncColorInputs() {
        const primaryInput = document.querySelector('[data-field="primary_color"]');
        const secondaryInput = document.querySelector('[data-field="secondary_color"]');
        if (primaryInput && state.siteState.primary_color) {
            primaryInput.value = state.siteState.primary_color;
        }
        if (secondaryInput && state.siteState.secondary_color) {
            secondaryInput.value = state.siteState.secondary_color;
        }
    }

    function setupPaletteControls() {
        const resetButton = document.getElementById('resetPaletteSelection');
        if (resetButton) {
            resetButton.addEventListener('click', () => {
                state.activePaletteId = null;
                renderPaletteSuggestions();
                showNotification('Modo de colores personalizados activado', 'info');
            });
        }
    }

    function updatePaletteState() {
        state.activePaletteId = detectActivePalette(state.siteState.model_type);
        renderPaletteSuggestions();
    }

    const IMAGE_MAX_BYTES = 6 * 1024 * 1024;
    const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/gif', 'image/svg+xml'];

    async function init() {
        const authed = await checkAuth();
        if (!authed) return;

        await loadModels();
        await loadSite();
        bindFieldInputs();
        setupPaletteControls();
        refreshPreview(true);
    }

    async function loadModels() {
        state.models = await loadBusinessModels();
        const select = document.getElementById('modelSelect');
        if (!select) return;
        select.innerHTML = state.models.map(model => `<option value="${model.id}">${getModelIcon(model.id)} ${model.name}</option>`).join('');
    }

    async function loadSite() {
        const response = await fetchAPI(`/api/sites/${state.siteId}`);
        if (!response?.ok) {
            showNotification('No se pudo cargar el sitio', 'error');
            return;
        }
    const site = await response.json();
    const products = safeParseArray(site.products || site.products_json);
    const gallery = safeParseArray(site.gallery_images);

        state.siteState = {
            model_type: site.model_type,
            name: site.name,
            description: site.description,
            hero_title: site.hero_title,
            hero_subtitle: site.hero_subtitle,
            hero_image: site.hero_image,
            about_text: site.about_text,
            about_image: site.about_image,
            contact_email: site.contact_email,
            contact_phone: site.contact_phone,
            contact_address: site.contact_address,
            whatsapp_number: site.whatsapp_number,
            facebook_url: site.facebook_url,
            instagram_url: site.instagram_url,
            tiktok_url: site.tiktok_url,
            logo_url: site.logo_url,
            primary_color: site.primary_color || '#8B5E3C',
            secondary_color: site.secondary_color || '#CBB67C',
            products,
            gallery_images: gallery,
            supporter_logos: safeParseArray(site.supporter_logos_json),
            custom_domain: site.custom_domain
        };

        canonicalizeSiteMedia();

        updateMeta(site);
        hydrateInputs();
        renderProducts();
        renderGallery();
        updatePaletteState();
    }

    function updateMeta(site) {
        const siteNameEl = document.getElementById('previewSiteName');
        const statusEl = document.getElementById('siteStatus');
        const modelEl = document.getElementById('siteModel');
        const updatedEl = document.getElementById('siteUpdatedAt');
        const breadcrumbEl = document.getElementById('editorBreadcrumb');
        const githubLink = document.getElementById('siteGithubLink');

        if (siteNameEl) siteNameEl.textContent = site.name || 'Sin nombre';
        if (statusEl) statusEl.textContent = site.is_published ? 'Publicado' : 'Borrador';
        if (modelEl) modelEl.textContent = getModelName(site.model_type);
        if (updatedEl) updatedEl.textContent = site.updated_at ? formatDate(site.updated_at) : '—';
        if (breadcrumbEl) breadcrumbEl.textContent = `Editando · ${site.name}`;
        if (githubLink) {
            if (site.github_url) {
                githubLink.textContent = site.github_url;
                githubLink.href = site.github_url;
            } else {
                githubLink.textContent = 'Sin publicar';
                githubLink.href = '#';
            }
        }
    }

    function hydrateInputs() {
        document.querySelectorAll('[data-field]').forEach(input => {
            const field = input.dataset.field;
            if (typeof state.siteState[field] !== 'undefined') {
                input.value = state.siteState[field] ?? '';
            } else if (input.type === 'color' && !state.siteState[field]) {
                input.value = '#FFFFFF';
            } else {
                input.value = '';
            }
        });

        const modelSelect = document.getElementById('modelSelect');
        if (modelSelect && state.siteState.model_type) {
            modelSelect.value = state.siteState.model_type;
        }
    }

    function bindFieldInputs() {
        if (state.inputsBound) return;
        document.querySelectorAll('[data-field]').forEach(input => {
            input.addEventListener('input', event => {
                updateField(event.target.dataset.field, event.target.value);
            });
        });
        state.inputsBound = true;
    }

    function updateField(field, value) {
        if (["logo_url", "hero_image", "about_image"].includes(field)) {
            value = canonicalizeAssetUrl(value);
        }
        state.siteState[field] = value;
        if (field === 'name') {
            const siteNameEl = document.getElementById('previewSiteName');
            if (siteNameEl) siteNameEl.textContent = value || 'Sin nombre';
        }
        if (field === 'model_type') {
            const modelEl = document.getElementById('siteModel');
            if (modelEl) modelEl.textContent = getModelName(value);
            state.activePaletteId = detectActivePalette(value);
            renderPaletteSuggestions(value);
        }
        if (field === 'primary_color' || field === 'secondary_color') {
            state.activePaletteId = detectActivePalette(state.siteState.model_type);
            renderPaletteSuggestions();
        }
        refreshPreview();
    }

    function renderProducts() {
        const container = document.getElementById('productsList');
        const empty = document.getElementById('productsEmpty');
        if (!container || !empty) return;

        if (!state.siteState.products || state.siteState.products.length === 0) {
            container.innerHTML = '';
            empty.classList.remove('hidden');
            return;
        }

        empty.classList.add('hidden');
        container.innerHTML = state.siteState.products.map((product, index) => `
            <article class="border border-gray-100 rounded-2xl p-4 space-y-3 bg-gray-50">
                <div class="flex items-start justify-between">
                    <h4 class="text-sm font-semibold text-gray-700">Producto ${index + 1}</h4>
                    <button type="button" class="text-xs text-red-500" onclick="editorVisual.removeProduct(${index})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <input type="text" class="input-control" value="${escapeAttr(product.name)}" placeholder="Nombre" oninput="editorVisual.updateProduct(${index}, 'name', this.value)">
                <textarea class="input-control" rows="2" placeholder="Descripción" oninput="editorVisual.updateProduct(${index}, 'description', this.value)">${escapeText(product.description)}</textarea>
                <div class="dual-inputs">
                    <input type="text" class="input-control" value="${escapeAttr(product.price)}" placeholder="Precio" oninput="editorVisual.updateProduct(${index}, 'price', this.value)">
                    <div class="space-y-2">
                        <div class="flex gap-2">
                            <input type="url" class="input-control flex-1" value="${escapeAttr(product.image)}" placeholder="Imagen (URL)" oninput="editorVisual.updateProduct(${index}, 'image', this.value)">
                            <button type="button" class="inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-gray-200 text-xs font-semibold text-gray-700 hover:bg-gray-50" onclick="editorVisual.uploadProductImage(${index})">
                                <i class="fas fa-upload"></i>
                                Subir
                            </button>
                        </div>
                        <p class="text-[11px] text-gray-400">Acepta PNG, JPG, WEBP y GIF.</p>
                    </div>
                </div>
            </article>
        `).join('');
    }

    function renderGallery() {
        const container = document.getElementById('galleryList');
        const empty = document.getElementById('galleryEmpty');
        if (!container || !empty) return;

        if (!state.siteState.gallery_images || state.siteState.gallery_images.length === 0) {
            container.innerHTML = '';
            empty.classList.remove('hidden');
            return;
        }

        empty.classList.add('hidden');
        container.innerHTML = state.siteState.gallery_images.map((url, index) => `
            <div class="flex items-center gap-2">
                <input type="url" class="input-control flex-1" value="${escapeAttr(url)}" placeholder="https://" oninput="editorVisual.updateGalleryImage(${index}, this.value)">
                <button type="button" class="text-xs text-red-500" onclick="editorVisual.removeGalleryImage(${index})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }

    function addProduct() {
        state.siteState.products = state.siteState.products || [];
        state.siteState.products.push({
            name: 'Nuevo Producto',
            description: 'Describe tu producto aquí',
            price: '',
            image: ''
        });
        renderProducts();
        refreshPreview();
    }

    function updateProduct(index, field, value) {
        if (!state.siteState.products[index]) return;
        if (field === 'image') {
            state.siteState.products[index][field] = canonicalizeAssetUrl(value);
        } else {
            state.siteState.products[index][field] = value;
        }
        refreshPreview();
    }

    function removeProduct(index) {
        state.siteState.products.splice(index, 1);
        renderProducts();
        refreshPreview();
    }

    function addGalleryImage() {
        const url = prompt('Pega la URL pública de la imagen', 'https://');
        if (!url || url.trim() === '' || url === 'https://') return;
        state.siteState.gallery_images = state.siteState.gallery_images || [];
        state.siteState.gallery_images.push(url.trim());
        renderGallery();
        refreshPreview();
        showNotification('Imagen agregada desde URL', 'success');
    }

    function addGalleryImageFromFile() {
        openImagePicker(async (file) => {
            const uploadedUrl = await uploadAssetFile(file);
            if (!uploadedUrl) return;
            state.siteState.gallery_images = state.siteState.gallery_images || [];
            state.siteState.gallery_images.push(uploadedUrl);
            renderGallery();
            refreshPreview(true);
            showNotification('Imagen agregada a la galería', 'success');
        });
    }

    function updateGalleryImage(index, value) {
        if (typeof state.siteState.gallery_images[index] === 'undefined') return;
        state.siteState.gallery_images[index] = canonicalizeAssetUrl(value);
        refreshPreview();
    }

    function removeGalleryImage(index) {
        state.siteState.gallery_images.splice(index, 1);
        renderGallery();
        refreshPreview();
    }

    function safeParseArray(value) {
        if (Array.isArray(value)) return value;
        if (!value) return [];
        try {
            const parsed = JSON.parse(value);
            return Array.isArray(parsed) ? parsed : [];
        } catch (error) {
            return [];
        }
    }

    function escapeAttr(value) {
        if (value === null || value === undefined) return '';
        return String(value).replace(/"/g, '&quot;').replace(/</g, '&lt;');
    }

    function escapeText(value) {
        if (value === null || value === undefined) return '';
        return String(value).replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function injectBaseTag(html) {
        const originBase = `${window.location.origin}/`;
        let transformed = html;
        if (!transformed.includes('<base')) {
            transformed = transformed.replace('<head>', `<head><base href="${originBase}">`);
        }

        if (!transformed.includes('preview-anchor-handler')) {
            const helperScript = `
<script id="preview-anchor-handler">
(function(){
    function handleAnchorClick(event){
        const link = event.target.closest('a[href^="#"]');
        if(!link)return;
        const hash = link.getAttribute('href') || '';
        if(hash.length <= 1)return;
        const targetId = hash.slice(1);
        const target = document.getElementById(targetId);
        if(!target)return;
        event.preventDefault();
        target.scrollIntoView({behavior:'smooth', block:'start'});
    }
    document.addEventListener('click', handleAnchorClick, {capture:true});
})();
</script>`;

            if (transformed.includes('</body>')) {
                transformed = transformed.replace('</body>', `${helperScript}</body>`);
            } else {
                transformed = `${transformed}${helperScript}`;
            }
        }

        return transformed;
    }

    function refreshPreview(force = false) {
        clearTimeout(state.previewTimer);
        const delay = force ? 10 : 250;
        state.previewTimer = setTimeout(async () => {
            const payload = {
                ...state.siteState,
                products: state.siteState.products || [],
                gallery_images: state.siteState.gallery_images || []
            };

            const response = await fetchAPI('/api/sites/preview', {
                method: 'POST',
                body: JSON.stringify(payload)
            });

            if (!response?.ok) {
                showNotification('No se pudo renderizar la vista previa', 'error');
                return;
            }
            const html = injectBaseTag(await response.text());
            const blob = new Blob([html], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const frame = document.getElementById('sitePreviewFrame');
            if (frame) {
                frame.src = url;
                frame.onload = () => {
                    URL.revokeObjectURL(url);
                    attachPreviewBridge(frame);
                };
            }
            const badge = document.getElementById('autoPreviewBadge');
            if (badge) badge.classList.remove('hidden');
        }, delay);
    }

    function attachPreviewBridge(frame) {
        try {
            const doc = frame?.contentDocument;
            if (!doc || doc.__wcPreviewBridge) return;
            doc.__wcPreviewBridge = true;
            const handler = (event) => {
                const anchor = findAnchor(event.target, doc);
                if (!anchor) return;
                const href = anchor.getAttribute('href') || '';
                if (!href.startsWith('#') || href.length <= 1) return;
                const targetId = href.slice(1);
                const target = doc.getElementById(targetId);
                if (!target) return;
                event.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            };
            doc.addEventListener('click', handler, true);
        } catch (error) {
            console.warn('preview bridge error', error);
        }
    }

    function findAnchor(node, rootDoc) {
        let current = node;
        while (current && current !== rootDoc) {
            if (current.tagName && current.tagName.toLowerCase() === 'a') {
                return current;
            }
            current = current.parentNode;
        }
        return null;
    }

    function openImagePicker(onFileSelect) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.style.display = 'none';
        document.body.appendChild(input);
        input.addEventListener('change', () => {
            const file = input.files?.[0];
            document.body.removeChild(input);
            if (file && typeof onFileSelect === 'function') {
                onFileSelect(file);
            }
        }, { once: true });
        input.click();
    }

    function validateImageFile(file) {
        if (!file.type.startsWith('image/')) {
            showNotification('El archivo seleccionado no es una imagen', 'error');
            return false;
        }
        if (!ACCEPTED_IMAGE_TYPES.includes(file.type)) {
            showNotification('Formato no soportado. Usa PNG, JPG, WEBP, GIF o SVG.', 'error');
            return false;
        }
        if (file.size > IMAGE_MAX_BYTES) {
            showNotification('La imagen supera los 6MB permitidos', 'error');
            return false;
        }
        return true;
    }

    async function uploadAssetFile(file) {
        if (!validateImageFile(file)) return null;
        const formData = new FormData();
        formData.append('file', file);
        formData.append('site_id', state.siteId);
        try {
            showNotification('Subiendo imagen...', 'info');
            const response = await fetchAPI('/api/upload-image', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (response.ok && data.success && data.url) {
                const canonical = canonicalizeAssetUrl(data.url);
                return canonical || data.url;
            }
            showNotification(data.detail || 'No se pudo subir la imagen', 'error');
        } catch (error) {
            console.error('uploadAssetFile', error);
            showNotification('Error al subir la imagen', 'error');
        }
        return null;
    }

    function handleFieldUpload(field) {
        openImagePicker(async (file) => {
            const uploadedUrl = await uploadAssetFile(file);
            if (!uploadedUrl) return;
            const canonical = canonicalizeAssetUrl(uploadedUrl);
            state.siteState[field] = canonical;
            const input = document.querySelector(`[data-field="${field}"]`);
            if (input) input.value = canonical;
            showNotification('Imagen guardada correctamente', 'success');
            refreshPreview(true);
        });
    }

    function uploadProductImage(index) {
        if (!state.siteState.products || !state.siteState.products[index]) return;
        openImagePicker(async (file) => {
            const uploadedUrl = await uploadAssetFile(file);
            if (!uploadedUrl) return;
            const canonical = canonicalizeAssetUrl(uploadedUrl);
            state.siteState.products[index].image = canonical;
            renderProducts();
            refreshPreview(true);
            showNotification('Imagen del producto actualizada', 'success');
        });
    }

    async function persistSiteState(notify = false) {
        const payload = {
            ...state.siteState,
            products: state.siteState.products || [],
            gallery_images: state.siteState.gallery_images || []
        };

        try {
            const response = await fetchAPI(`/api/sites/${state.siteId}`, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
            if (response?.ok) {
                if (notify) {
                    showNotification('Cambios guardados', 'success');
                }
                return true;
            }
            if (notify) {
                showNotification('Error al guardar', 'error');
            }
        } catch (error) {
            console.error(error);
            if (notify) {
                showNotification('Error al guardar', 'error');
            }
        }
        return false;
    }

    async function saveSite() {
        const saved = await persistSiteState(true);
        if (saved) {
            await loadSite();
        }
    }

    async function publishSite() {
        if (!confirm('¿Deseas publicar este sitio en GitHub Pages?')) return;
        showNotification('Guardando cambios...', 'info');
        const saved = await persistSiteState(false);
        if (!saved) {
            showNotification('No se pudo guardar el sitio antes de publicar', 'error');
            return;
        }
        showNotification('Publicando sitio...', 'info');
        try {
            const response = await fetchAPI(`/api/sites/${state.siteId}/publish`, { method: 'POST' });
            const data = await response.json();
            if (response.ok) {
                showNotification('Sitio publicado', 'success');
                if (data.url) {
                    document.getElementById('siteGithubLink').textContent = data.url;
                    document.getElementById('siteGithubLink').href = data.url;
                }
                await loadSite();
            } else {
                showNotification(data.detail || 'Error al publicar', 'error');
            }
        } catch (error) {
            console.error(error);
            showNotification('Error al publicar', 'error');
        }
    }

    return {
        init,
        refreshPreview,
        saveSite,
        publishSite,
        addProduct,
        updateProduct,
        removeProduct,
        addGalleryImage,
        addGalleryImageFromFile,
        updateGalleryImage,
        removeGalleryImage,
        handleFieldUpload,
        uploadProductImage
    };
})();

document.addEventListener('DOMContentLoaded', editorVisual.init);
window.editorVisual = editorVisual;
