(function () {
  const numberFormatter = new Intl.NumberFormat("es-ES");
  const state = {
    initialized: false,
    users: [],
    filteredUsers: [],
    currentPage: 1,
    pageSize: 10,
    activeFilter: "all",
    searchTerm: "",
    editingUserId: null,
    sites: [],
    avatarUploading: false,
  };

  const AVATAR_ACCEPTED_TYPES = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/svg+xml",
  ];
  const AVATAR_MAX_BYTES = 5 * 1024 * 1024;
  const AVATAR_STATUS_CLASSES = [
    "text-slate-500",
    "text-slate-600",
    "text-emerald-600",
    "text-amber-600",
    "text-rose-600",
  ];

  let dom = {};

  function queryDom() {
    const container = document.getElementById("usersManagementView");
    if (!container) return {};
    return {
      container,
      search: container.querySelector("#umSearch"),
      tableBody: container.querySelector("#umUsersTableBody"),
      pageInfo: container.querySelector("#umPageInfo"),
      prevPage: container.querySelector("#umPrevPageBtn"),
      nextPage: container.querySelector("#umNextPageBtn"),
      pageSize: container.querySelector("#umPageSize"),
      filterChips: Array.from(container.querySelectorAll(".wc-filter-chip")),
      newUserBtn: container.querySelector("#umNewUserBtn"),
      drawer: container.querySelector("#umDrawer"),
      drawerTitle: container.querySelector("#umDrawerTitle"),
      closeDrawer: container.querySelector("#umCloseDrawerBtn"),
      cancelBtn: container.querySelector("#umCancelBtn"),
      saveBtn: container.querySelector("#umSaveBtn"),
      form: container.querySelector("#umForm"),
      username: container.querySelector("#umUsername"),
      email: container.querySelector("#umEmail"),
      password: container.querySelector("#umPassword"),
      role: container.querySelector("#umRole"),
      siteField: container.querySelector("#umSiteField"),
      siteSelect: container.querySelector("#umSiteId"),
      expiresAt: container.querySelector("#umExpiresAt"),
      isActive: container.querySelector("#umIsActive"),
      metaSection: container.querySelector("#umUserMetaSection"),
      meta: {
        id: container.querySelector("#umMetaId"),
        role: container.querySelector("#umMetaRole"),
        site: container.querySelector("#umMetaSite"),
        status: container.querySelector("#umMetaStatus"),
        lastLogin: container.querySelector("#umMetaLastLogin"),
        created: container.querySelector("#umMetaCreated"),
        updated: container.querySelector("#umMetaUpdated"),
        expires: container.querySelector("#umMetaExpires"),
        password: container.querySelector("#umMetaPassword"),
      },
      copyPasswordBtn: container.querySelector("#umCopyPasswordBtn"),
      avatar: {
        preview: container.querySelector("#umAvatarPreview"),
        image: container.querySelector("#umAvatarImage"),
        initials: container.querySelector("#umAvatarInitials"),
        status: container.querySelector("#umAvatarStatus"),
        uploadBtn: container.querySelector("#umAvatarUploadBtn"),
        resetBtn: container.querySelector("#umAvatarResetBtn"),
        input: container.querySelector("#umAvatarInput"),
        urlInput: container.querySelector("#umAvatarUrl"),
      },
      metrics: {
        total: container.querySelector("#umMetricTotal"),
        active: container.querySelector("#umMetricActive"),
        owners: container.querySelector("#umMetricOwners"),
      },
    };
  }

  function formatDate(dateString) {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  function formatDateTime(dateString) {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return date.toLocaleString("es-ES", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  }

  function toInputDateValue(dateString) {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toISOString().slice(0, 16);
  }

  function inputDateToISOString(value) {
    if (!value) return null;
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date.toISOString();
  }

  function formatInteger(value) {
    return numberFormatter.format(value ?? 0);
  }

  function getInitials(name = "") {
    return (
      name
        .split(" ")
        .map((n) => n[0] || "")
        .join("")
        .toUpperCase()
        .slice(0, 2) || "?"
    );
  }

  function escapeHtml(value = "") {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function resolveAvatarUrl(value = "") {
    const trimmed = (value || "").trim();
    if (!trimmed) return "";
    if (/^https?:\/\//i.test(trimmed) || trimmed.startsWith("data:")) {
      return trimmed;
    }
    if (trimmed.startsWith("/")) {
      return trimmed;
    }
    return `/images/${trimmed}`;
  }

  function getRoleBadge(role) {
    const badges = {
      superadmin: '<span class="wc-chip wc-chip--danger">Superadmin</span>',
      admin: '<span class="wc-chip wc-chip--warning">Administrador</span>',
      owner: '<span class="wc-chip wc-chip--success">Owner</span>',
    };
    return (
      badges[role] ||
      `<span class="wc-chip wc-chip--muted">${role || "—"}</span>`
    );
  }

  function getStatusBadge(user) {
    const now = new Date();
    const isExpired = user.expires_at ? new Date(user.expires_at) < now : false;
    if (!user.is_active) {
      return '<span class="wc-chip wc-chip--danger">Suspendido</span>';
    }
    if (isExpired) {
      return '<span class="wc-chip wc-chip--warning">Expirado</span>';
    }
    return '<span class="wc-chip wc-chip--success">Activo</span>';
  }

  function getSiteChip(user) {
    if (user.site && user.site.name) {
      return `<span class="wc-chip wc-chip--muted"><i class="fa-solid fa-earth-americas mr-1"></i>${user.site.name}</span>`;
    }
    return '<span class="wc-chip wc-chip--muted"><i class="fa-regular fa-circle mr-1"></i>Sin sitio asignado</span>';
  }

  function getAvatarMarkup(user) {
    const initials = getInitials(user.username);
    if (user.avatar_url) {
      const url = escapeHtml(resolveAvatarUrl(user.avatar_url));
      const alt = escapeHtml(user.username || "Usuario WebControl");
      return `
        <div class="w-12 h-12 rounded-full ring-2 ring-slate-100 overflow-hidden bg-slate-100 flex items-center justify-center">
          <img src="${url}" alt="${alt}" class="w-full h-full object-cover" />
        </div>
      `;
    }
    return `
      <div class="w-12 h-12 rounded-full ring-2 ring-slate-100 bg-slate-100 flex items-center justify-center font-semibold text-slate-600">
        ${initials}
      </div>
    `;
  }

  function renderRow(user) {
    const avatarMarkup = getAvatarMarkup(user);
    const activationDate = formatDate(user.activated_at);
    const expirationDate = formatDate(user.expires_at);
    const lastLogin = formatDateTime(user.last_login);
    const roleBadge = getRoleBadge(user.role);
    const statusBadge = getStatusBadge(user);
    const siteChip = getSiteChip(user);
    const idChip = `<span class="wc-chip wc-chip--muted">ID #${user.id}</span>`;
    const roleDescriptor = user.role_display || user.role_label;

    return `
      <tr>
        <td class="align-top">
          <div class="flex items-center gap-3">
            ${avatarMarkup}
            <div>
              <div class="text-sm font-semibold text-slate-900">${
                user.username
              }</div>
              <div class="text-xs text-slate-500">${user.email || "—"}</div>
              <div class="mt-2 flex flex-wrap gap-2 text-xs">${siteChip}${idChip}</div>
            </div>
          </div>
        </td>
        <td class="align-top text-sm">
          ${roleBadge}
          ${
            roleDescriptor
              ? `<p class="text-xs text-slate-500 mt-1">${roleDescriptor}</p>`
              : ""
          }
        </td>
        <td class="align-top text-sm">${statusBadge}</td>
        <td class="align-top text-sm text-slate-900">${activationDate}</td>
        <td class="align-top text-sm text-slate-900">${expirationDate}</td>
        <td class="align-top text-sm text-slate-900">${lastLogin}</td>
        <td class="align-top">
          <div class="flex gap-2">
            <button class="table-action" type="button" data-action="edit" data-user-id="${
              user.id
            }">
              <i class="fa-solid fa-pen-to-square"></i>
            </button>
            <button class="table-action table-action--danger" type="button" data-action="delete" data-user-id="${
              user.id
            }">
              <i class="fa-solid fa-trash"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }

  function updatePagination() {
    if (!dom.pageInfo) return;
    const total = state.filteredUsers.length;
    const totalPages = Math.ceil(total / state.pageSize) || 1;
    const start = total ? (state.currentPage - 1) * state.pageSize + 1 : 0;
    const end = total ? Math.min(state.currentPage * state.pageSize, total) : 0;
    dom.pageInfo.textContent = total
      ? `Mostrando ${start}-${end} de ${total} usuarios`
      : "Mostrando 0 de 0 usuarios";
    if (dom.prevPage) {
      dom.prevPage.disabled = state.currentPage === 1 || total === 0;
    }
    if (dom.nextPage) {
      dom.nextPage.disabled = state.currentPage >= totalPages || total === 0;
    }
  }

  function updateTable() {
    if (!dom.tableBody) return;
    const start = (state.currentPage - 1) * state.pageSize;
    const pageUsers = state.filteredUsers.slice(start, start + state.pageSize);
    if (!pageUsers.length) {
      dom.tableBody.innerHTML = `
        <tr>
          <td colspan="7">
            <div class="wc-empty-state">
              <h4>No hay coincidencias</h4>
              <p>Ajusta la búsqueda o crea un nuevo usuario.</p>
            </div>
          </td>
        </tr>
      `;
    } else {
      dom.tableBody.innerHTML = pageUsers.map(renderRow).join("");
    }
    updatePagination();
  }

  function applyFilters() {
    const query = state.searchTerm;
    state.filteredUsers = state.users.filter((user) => {
      const matchesSearch = [user.username, user.email, user.role]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(query);
      if (!matchesSearch) return false;
      switch (state.activeFilter) {
        case "owners":
          return (user.role || "").toLowerCase() === "owner";
        case "admins":
          return (user.role || "").toLowerCase() === "admin";
        case "suspended":
          return !user.is_active;
        default:
          return true;
      }
    });
    state.currentPage = 1;
    updateTable();
  }

  function updateMetrics() {
    if (!dom.metrics) return;
    const metrics = {
      total: state.users.length,
      active: state.users.filter(
        (user) =>
          user.is_active &&
          (!user.expires_at || new Date(user.expires_at) >= new Date())
      ).length,
      owners: state.users.filter(
        (user) => (user.role || "").toLowerCase() === "owner"
      ).length,
    };
    Object.entries(metrics).forEach(([key, value]) => {
      const element = dom.metrics[key];
      if (!element) return;
      element.textContent = formatInteger(value);
      element.classList.remove("metric-bump");
      void element.offsetWidth;
      element.classList.add("metric-bump");
    });
  }

  async function loadUsers() {
    try {
      const response = await fetchAPI("/api/users");
      if (!response || !response.ok) {
        throw new Error("Error al cargar usuarios");
      }
      state.users = await response.json();
      state.filteredUsers = [...state.users];
      updateMetrics();
      applyFilters();
    } catch (error) {
      console.error("Error loading users:", error);
      showNotification("Error al cargar usuarios", "error");
    }
  }

  async function loadSites() {
    try {
      const response = await fetchAPI("/api/sites");
      if (!response || !response.ok) {
        throw new Error("Error al cargar sitios");
      }
      state.sites = await response.json();
      populateSiteOptions();
    } catch (error) {
      console.error("Error loading sites:", error);
    }
  }

  function populateSiteOptions() {
    if (!dom.siteSelect) return;
    dom.siteSelect.innerHTML = '<option value="">Seleccionar sitio</option>';
    state.sites.forEach((site) => {
      const option = document.createElement("option");
      option.value = site.id;
      option.textContent = site.name || `Sitio #${site.id}`;
      dom.siteSelect.appendChild(option);
    });
  }

  function setAvatarStatus(message, variant = "muted") {
    const statusEl = dom.avatar?.status;
    if (!statusEl) return;
    const tones = {
      muted: "text-slate-500",
      info: "text-slate-600",
      success: "text-emerald-600",
      warning: "text-amber-600",
      error: "text-rose-600",
    };
    AVATAR_STATUS_CLASSES.forEach((cls) => statusEl.classList.remove(cls));
    statusEl.textContent = message || statusEl.dataset.defaultMessage || "";
    statusEl.classList.add(tones[variant] || tones.muted);
  }

  function updateAvatarPreview(avatarUrl, username) {
    if (!dom.avatar) return;
    const imageEl = dom.avatar.image;
    const initialsEl = dom.avatar.initials;
    const resolved = resolveAvatarUrl(avatarUrl);
    const hasImage = Boolean(resolved);
    if (hasImage && imageEl) {
      imageEl.classList.remove("hidden");
      imageEl.src = resolved;
      initialsEl?.classList.add("hidden");
    } else {
      if (imageEl) {
        imageEl.classList.add("hidden");
        imageEl.removeAttribute("src");
      }
      if (initialsEl) {
        initialsEl.classList.remove("hidden");
        initialsEl.textContent = getInitials(username);
      }
    }
  }

  function setAvatarUploading(isUploading) {
    state.avatarUploading = Boolean(isUploading);
    if (!dom.avatar) return;
    const { uploadBtn, resetBtn } = dom.avatar;
    const defaultLabel =
      uploadBtn?.dataset.defaultLabel ||
      "<i class='fa-solid fa-cloud-arrow-up'></i> Subir imagen";
    if (uploadBtn) {
      uploadBtn.disabled = state.avatarUploading;
      uploadBtn.classList.toggle("opacity-60", state.avatarUploading);
      uploadBtn.innerHTML = state.avatarUploading
        ? "<i class='fa-solid fa-circle-notch fa-spin'></i> Subiendo..."
        : defaultLabel;
    }
    if (resetBtn) {
      resetBtn.disabled = state.avatarUploading;
      resetBtn.classList.toggle("opacity-60", state.avatarUploading);
    }
  }

  function resetAvatarPreview() {
    if (!dom.avatar) return;
    if (dom.avatar.input) dom.avatar.input.value = "";
    if (dom.avatar.urlInput) dom.avatar.urlInput.value = "";
    setAvatarUploading(false);
    updateAvatarPreview("", dom.username?.value || "");
    setAvatarStatus(dom.avatar.status?.dataset.defaultMessage || "");
  }

  function validateAvatarFile(file) {
    if (!file) {
      showNotification("Selecciona un archivo válido", "warning");
      return false;
    }
    if (!file.type || !file.type.startsWith("image/")) {
      showNotification("El archivo seleccionado no es una imagen", "error");
      setAvatarStatus("El archivo seleccionado no es una imagen", "error");
      return false;
    }
    if (!AVATAR_ACCEPTED_TYPES.includes(file.type)) {
      showNotification(
        "Formato no soportado. Usa JPG, PNG, GIF, WebP o SVG",
        "error"
      );
      setAvatarStatus("Formato de imagen no soportado", "error");
      return false;
    }
    if (file.size > AVATAR_MAX_BYTES) {
      showNotification("La imagen supera los 5MB permitidos", "error");
      setAvatarStatus("La imagen supera los 5MB permitidos", "error");
      return false;
    }
    return true;
  }

  async function uploadAvatarFile(file) {
    if (state.avatarUploading) {
      showNotification("Ya hay una carga en progreso", "info");
      if (dom.avatar?.input) dom.avatar.input.value = "";
      return null;
    }
    if (!validateAvatarFile(file)) {
      if (dom.avatar?.input) dom.avatar.input.value = "";
      return null;
    }
    const formData = new FormData();
    formData.append("file", file);
    setAvatarUploading(true);
    setAvatarStatus("Subiendo imagen...", "info");
    try {
      const response = await fetchAPI("/api/upload-image", {
        method: "POST",
        body: formData,
      });
      if (!response) {
        throw new Error("Sin respuesta del servidor");
      }
      const data = await response.json();
      if (!response.ok || !data?.url) {
        throw new Error(data?.detail || "No se pudo subir la imagen");
      }
      const url = data.url;
      if (dom.avatar?.urlInput) {
        dom.avatar.urlInput.value = url;
      }
      updateAvatarPreview(url, dom.username?.value || "");
      setAvatarStatus("Imagen actualizada correctamente", "success");
      showNotification("Foto de perfil actualizada", "success");
      return url;
    } catch (error) {
      console.error("uploadAvatarFile", error);
      setAvatarStatus("No se pudo subir la imagen", "error");
      showNotification("No se pudo subir la imagen", "error");
      return null;
    } finally {
      setAvatarUploading(false);
      if (dom.avatar?.input) dom.avatar.input.value = "";
    }
  }

  function handleAvatarFileChange(event) {
    const file = event.target?.files?.[0];
    if (!file) return;
    uploadAvatarFile(file);
  }

  function handleAvatarReset() {
    if (!dom.avatar) return;
    resetAvatarPreview();
    showNotification("Se quitó la foto de perfil", "info");
  }

  function showDrawer(title, user = null) {
    if (!dom.drawer || !dom.form) return;
    dom.drawerTitle.textContent = title;
    dom.drawer.classList.remove("hidden");
    dom.form.reset();
    resetAvatarPreview();
    state.editingUserId = user ? user.id : null;
    dom.password.required = !user;
    dom.password.value = "";
    dom.isActive.checked = true;
    dom.expiresAt.value = "";
    dom.role.value = "";
    dom.siteSelect.value = "";
    toggleSiteField("");
    if (user) {
      dom.username.value = user.username || "";
      dom.email.value = user.email || "";
      dom.role.value = user.role || "";
      dom.siteSelect.value = user.site_id || "";
      dom.expiresAt.value = toInputDateValue(user.expires_at);
      dom.isActive.checked = Boolean(user.is_active);
      toggleSiteField(dom.role.value);
    }
    if (dom.avatar?.urlInput) {
      const avatarValue = user?.avatar_url || "";
      dom.avatar.urlInput.value = avatarValue;
      updateAvatarPreview(
        avatarValue,
        user?.username || dom.username?.value || ""
      );
      setAvatarStatus(
        avatarValue
          ? "Usando la foto almacenada para este usuario."
          : dom.avatar.status?.dataset.defaultMessage || ""
      );
    }
    updateUserMeta(user);
  }

  function hideDrawer() {
    if (!dom.drawer || !dom.form) return;
    dom.drawer.classList.add("hidden");
    dom.form.reset();
    dom.password.required = true;
    state.editingUserId = null;
    resetAvatarPreview();
    updateUserMeta(null);
  }

  function toggleSiteField(roleValue) {
    if (!dom.siteField || !dom.siteSelect) return;
    const isOwner = roleValue === "owner";
    dom.siteField.classList.toggle("hidden", !isOwner);
    dom.siteSelect.required = isOwner;
  }

  function updateUserMeta(user) {
    if (!dom.metaSection || !dom.meta) return;
    if (!user) {
      dom.metaSection.classList.add("hidden");
      Object.values(dom.meta).forEach((element) => {
        if (element) element.textContent = "—";
      });
      if (dom.copyPasswordBtn) {
        dom.copyPasswordBtn.disabled = true;
        dom.copyPasswordBtn.dataset.password = "";
      }
      return;
    }

    dom.metaSection.classList.remove("hidden");
    dom.meta.id.textContent = `#${user.id}`;
    dom.meta.role.textContent =
      user.role_display || user.role_label || user.role || "—";
    dom.meta.site.textContent =
      user.site && user.site.name ? user.site.name : "Sin sitio asignado";
    dom.meta.status.innerHTML = getStatusBadge(user);
    dom.meta.lastLogin.textContent = formatDateTime(user.last_login);
    dom.meta.created.textContent = formatDateTime(user.created_at);
    dom.meta.updated.textContent = formatDateTime(user.updated_at);
    dom.meta.expires.textContent = formatDateTime(user.expires_at);
    const plainPassword = user.plain_password || "—";
    dom.meta.password.textContent = plainPassword;
    if (dom.copyPasswordBtn) {
      dom.copyPasswordBtn.disabled = !user.plain_password;
      dom.copyPasswordBtn.dataset.password = user.plain_password || "";
    }
  }

  async function handleUserSubmit() {
    if (!dom.form) return;
    const formData = new FormData(dom.form);
    const isEditing = Boolean(state.editingUserId);
    const rawPassword = (formData.get("password") || "").trim();
    const siteIdValue = formData.get("site_id");
    const avatarValue = (formData.get("avatar_url") || "").toString().trim();
    const emailValue = (formData.get("email") || "").trim();
    const payload = {
      username: (formData.get("username") || "").trim(),
      email: emailValue || null,
      role: formData.get("role"),
      site_id: siteIdValue ? Number(siteIdValue) : null,
      expires_at: inputDateToISOString(formData.get("expires_at")),
      is_active: Boolean(dom.isActive?.checked),
      avatar_url: avatarValue || null,
    };

    if (!payload.username || !payload.role) {
      showNotification("Ingresa al menos usuario y rol", "warning");
      return;
    }

    if ((!isEditing || rawPassword) && rawPassword.length < 8) {
      showNotification(
        "La contraseña debe tener al menos 8 caracteres",
        "warning"
      );
      return;
    }

    if (!isEditing || rawPassword) {
      payload.password = rawPassword;
    }

    try {
      let response;
      if (isEditing) {
        response = await fetchAPI(`/api/users/${state.editingUserId}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });
      } else {
        response = await fetchAPI("/api/users", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }

      if (!response || !response.ok) {
        throw new Error("Error al guardar usuario");
      }

      hideDrawer();
      await loadUsers();
      showNotification("Usuario guardado correctamente", "success");
    } catch (error) {
      console.error("Error saving user:", error);
      showNotification("No se pudo guardar el usuario", "error");
    }
  }

  async function deleteUser(userId) {
    const confirmed = await confirmAction("¿Eliminar este usuario?", {
      title: "Eliminar usuario",
      icon: "warning",
      confirmText: "Sí, eliminar",
    });
    if (!confirmed) return;

    try {
      const response = await fetchAPI(`/api/users/${userId}`, {
        method: "DELETE",
      });
      if (!response || !response.ok) {
        throw new Error("Error al eliminar usuario");
      }
      await loadUsers();
      showNotification("Usuario eliminado", "success");
    } catch (error) {
      console.error("Error deleting user:", error);
      showNotification("No se pudo eliminar el usuario", "error");
    }
  }

  function handleTableActionClick(event) {
    const actionBtn = event.target.closest("[data-action]");
    if (!actionBtn) return;
    const userId = Number(actionBtn.dataset.userId);
    if (!userId) return;
    if (actionBtn.dataset.action === "edit") {
      const user = state.users.find((item) => item.id === userId);
      if (user) showDrawer("Editar Usuario", user);
      return;
    }
    if (actionBtn.dataset.action === "delete") {
      deleteUser(userId);
    }
  }

  function bindEvents() {
    dom.search?.addEventListener("input", (event) => {
      state.searchTerm = (event.target.value || "").toLowerCase();
      applyFilters();
    });

    dom.filterChips.forEach((chip) => {
      chip.addEventListener("click", () => {
        dom.filterChips.forEach((item) => item.classList.remove("active"));
        chip.classList.add("active");
        state.activeFilter = chip.dataset.filter || "all";
        applyFilters();
      });
    });

    dom.pageSize?.addEventListener("change", (event) => {
      state.pageSize = parseInt(event.target.value, 10) || 10;
      state.currentPage = 1;
      updateTable();
    });

    dom.prevPage?.addEventListener("click", () => {
      if (state.currentPage === 1) return;
      state.currentPage -= 1;
      updateTable();
    });

    dom.nextPage?.addEventListener("click", () => {
      const totalPages =
        Math.ceil(state.filteredUsers.length / state.pageSize) || 1;
      if (state.currentPage >= totalPages) return;
      state.currentPage += 1;
      updateTable();
    });

    dom.newUserBtn?.addEventListener("click", () =>
      showDrawer("Nuevo Usuario")
    );
    dom.saveBtn?.addEventListener("click", handleUserSubmit);
    dom.cancelBtn?.addEventListener("click", hideDrawer);
    dom.closeDrawer?.addEventListener("click", hideDrawer);
    dom.role?.addEventListener("change", (event) =>
      toggleSiteField(event.target.value)
    );
    dom.tableBody?.addEventListener("click", handleTableActionClick);

    dom.copyPasswordBtn?.addEventListener("click", async () => {
      const value = dom.copyPasswordBtn.dataset.password;
      if (!value) return;
      try {
        await navigator.clipboard.writeText(value);
        showNotification("Contraseña copiada al portapapeles", "success");
      } catch (error) {
        console.error("Clipboard error:", error);
        showNotification("No se pudo copiar la contraseña", "error");
      }
    });

    dom.drawer?.addEventListener("click", (event) => {
      if (event.target === dom.drawer) {
        hideDrawer();
      }
    });

    dom.avatar?.uploadBtn?.addEventListener("click", () => {
      dom.avatar.input?.click();
    });
    dom.avatar?.input?.addEventListener("change", handleAvatarFileChange);
    dom.avatar?.resetBtn?.addEventListener("click", handleAvatarReset);
    dom.username?.addEventListener("input", () => {
      const currentAvatar = dom.avatar?.urlInput?.value || "";
      updateAvatarPreview(currentAvatar, dom.username.value || "");
    });
  }

  async function activate() {
    if (state.initialized) {
      if (!state.users.length) {
        await loadUsers();
      }
      return;
    }

    dom = queryDom();
    if (!dom.container) return;
    state.pageSize = Number(dom.pageSize?.value || 10);
    bindEvents();
    state.initialized = true;
    await Promise.all([loadUsers(), loadSites()]);
  }

  window.UsersModule = { activate };
})();
