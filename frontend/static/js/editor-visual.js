const editorVisual = (() => {
    const state = {
        siteId: window.__SITE_ID__,
        siteState: {
            products: [],
            gallery_images: []
        },
        previewTimer: null,
        models: [],
        inputsBound: false
    };

    async function init() {
        const authed = await checkAuth();
        if (!authed) return;

        await loadModels();
        await loadSite();
        bindFieldInputs();
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

        updateMeta(site);
        hydrateInputs();
        renderProducts();
        renderGallery();
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
        state.siteState[field] = value;
        if (field === 'name') {
            const siteNameEl = document.getElementById('previewSiteName');
            if (siteNameEl) siteNameEl.textContent = value || 'Sin nombre';
        }
        if (field === 'model_type') {
            const modelEl = document.getElementById('siteModel');
            if (modelEl) modelEl.textContent = getModelName(value);
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
                    <input type="url" class="input-control" value="${escapeAttr(product.image)}" placeholder="Imagen (URL)" oninput="editorVisual.updateProduct(${index}, 'image', this.value)">
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
        state.siteState.products[index][field] = value;
        refreshPreview();
    }

    function removeProduct(index) {
        state.siteState.products.splice(index, 1);
        renderProducts();
        refreshPreview();
    }

    function addGalleryImage() {
        state.siteState.gallery_images = state.siteState.gallery_images || [];
        state.siteState.gallery_images.push('https://');
        renderGallery();
        refreshPreview();
    }

    function updateGalleryImage(index, value) {
        if (typeof state.siteState.gallery_images[index] === 'undefined') return;
        state.siteState.gallery_images[index] = value;
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
        if (!html.includes('<base')) {
            return html.replace('<head>', '<head><base href="/">');
        }
        return html;
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
                frame.onload = () => URL.revokeObjectURL(url);
            }
            const badge = document.getElementById('autoPreviewBadge');
            if (badge) badge.classList.remove('hidden');
        }, delay);
    }

    async function saveSite() {
        const payload = {
            ...state.siteState,
            products: state.siteState.products,
            gallery_images: state.siteState.gallery_images
        };

        try {
            const response = await fetchAPI(`/api/sites/${state.siteId}`, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
            if (response.ok) {
                showNotification('Cambios guardados', 'success');
                await loadSite();
            } else {
                showNotification('Error al guardar', 'error');
            }
        } catch (error) {
            console.error(error);
            showNotification('Error al guardar', 'error');
        }
    }

    async function publishSite() {
        if (!confirm('¿Deseas publicar este sitio en GitHub Pages?')) return;
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
        updateGalleryImage,
        removeGalleryImage
    };
})();

document.addEventListener('DOMContentLoaded', editorVisual.init);
window.editorVisual = editorVisual;
