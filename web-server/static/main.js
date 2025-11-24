// ======================
// CONFIGURACIÓN DINÁMICA
// ======================
let CONFIG = {
  auth_server_url: "http://localhost:5000", // Valor por defecto
  web_server_url: window.location.origin, // Origen actual
};

// Cargar configuración desde el backend
async function loadConfig() {
  try {
    const res = await fetch("/api/config");
    if (res.ok) {
      const data = await res.json();
      CONFIG = {
        auth_server_url: data.auth_server_url,
        web_server_url: data.web_server_url || window.location.origin,
      };
      console.log("✓ Configuración cargada:", CONFIG);
    }
  } catch (err) {
    console.warn(
      "⚠ No se pudo cargar configuración, usando valores por defecto"
    );
  }
}

// Cargar configuración al inicio
loadConfig();

// Para compatibilidad con código existente
const API_BASE = ""; // mismo dominio
// Función helper para obtener AUTH_URL dinámicamente
const getAuthURL = () => CONFIG.auth_server_url;

// ======================
// UTILIDADES
// ======================
function showAlert(elementId, message, isError = false) {
  const alert = document.getElementById(elementId);
  const textElement = document.getElementById(elementId + "Text");

  if (alert && textElement) {
    textElement.textContent = message;
    alert.classList.remove("d-none");

    // Auto-ocultar después de 5 segundos
    setTimeout(() => {
      alert.classList.add("d-none");
    }, 5000);
  }
}

function hideAlert(elementId) {
  const alert = document.getElementById(elementId);
  if (alert) {
    alert.classList.add("d-none");
  }
}

function formatDate(dateString) {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleDateString("es-ES", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function formatCurrency(value) {
  return new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

// ======================
// AUTENTICACIÓN
// ======================
document.addEventListener("DOMContentLoaded", () => {
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.onclick = () => {
      localStorage.removeItem("token");
      window.location.href = "/login";
    };
  }
});

// Login
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("loginUsername").value;
    const password = document.getElementById("loginPassword").value;
    const errorDiv = document.getElementById("loginError");
    const errorText = document.getElementById("loginErrorText");

    hideAlert("loginError");

    try {
      const res = await fetch(`${getAuthURL()}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        errorText.textContent =
          data.error || data.message || "Credenciales incorrectas";
        errorDiv.classList.remove("d-none");
        return;
      }

      localStorage.setItem("token", data.token);
      window.location.href = "/dashboard";
    } catch (err) {
      errorText.textContent =
        "Error de conexión con el servidor de autenticación";
      errorDiv.classList.remove("d-none");
    }
  });
}

// Register
const registerForm = document.getElementById("registerForm");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("registerUsername").value;
    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;
    const passwordConfirm = document.getElementById(
      "registerPasswordConfirm"
    ).value;
    const errorDiv = document.getElementById("registerError");
    const errorText = document.getElementById("registerErrorText");
    const successDiv = document.getElementById("registerSuccess");
    const successText = document.getElementById("registerSuccessText");

    hideAlert("registerError");
    hideAlert("registerSuccess");

    // Validaciones del lado del cliente
    if (username.length < 3) {
      errorText.textContent = "El usuario debe tener al menos 3 caracteres";
      errorDiv.classList.remove("d-none");
      return;
    }

    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      errorText.textContent =
        "El usuario solo puede contener letras, números y guiones bajos";
      errorDiv.classList.remove("d-none");
      return;
    }

    if (password.length < 6) {
      errorText.textContent = "La contraseña debe tener al menos 6 caracteres";
      errorDiv.classList.remove("d-none");
      return;
    }

    if (password !== passwordConfirm) {
      errorText.textContent = "Las contraseñas no coinciden";
      errorDiv.classList.remove("d-none");
      return;
    }

    try {
      const res = await fetch(`${getAuthURL()}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          email,
          password,
          role: "user", // Rol por defecto
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        errorText.textContent =
          data.error || data.message || "Error al registrar usuario";
        errorDiv.classList.remove("d-none");
        return;
      }

      // Mostrar mensaje de éxito
      successText.textContent =
        "¡Cuenta creada exitosamente! Redirigiendo al login...";
      successDiv.classList.remove("d-none");

      // Limpiar formulario
      registerForm.reset();

      // Redirigir al login después de 2 segundos
      setTimeout(() => {
        // Cambiar al tab de login
        const loginTab = document.getElementById("login-tab");
        if (loginTab) {
          loginTab.click();
        }
        hideAlert("registerSuccess");
      }, 2000);
    } catch (err) {
      errorText.textContent =
        "Error de conexión con el servidor de autenticación";
      errorDiv.classList.remove("d-none");
    }
  });
}

// ======================
// PRODUCTOS - DASHBOARD
// ======================
async function loadProducts() {
  const tbody = document.getElementById("productsTable");
  if (!tbody) return;

  const token = localStorage.getItem("token");
  const loadingSpinner = document.getElementById("loadingSpinner");
  const productsContainer = document.getElementById("productsContainer");
  const emptyState = document.getElementById("emptyState");

  try {
    const res = await fetch("/products", {
      headers: { Authorization: `Bearer ${token}` },
    });

    const data = await res.json();

    if (!res.ok) {
      showAlert("errorGlobal", data.message, true);
      return;
    }

    // Ocultar spinner
    if (loadingSpinner) loadingSpinner.classList.add("d-none");

    // Mostrar tabla o estado vacío
    if (data.products.length === 0) {
      if (emptyState) emptyState.classList.remove("d-none");
      if (productsContainer) productsContainer.classList.add("d-none");
    } else {
      if (emptyState) emptyState.classList.add("d-none");
      if (productsContainer) productsContainer.classList.remove("d-none");

      tbody.innerHTML = "";

      data.products.forEach((p) => {
        const stockBadge =
          p.stock < 10
            ? `<span class="badge badge-danger">${p.stock}</span>`
            : `<span class="badge badge-success">${p.stock}</span>`;

        tbody.innerHTML += `
          <tr>
            <td><strong>${p.name}</strong><br><small class="text-muted">${
          p.description || ""
        }</small></td>
            <td>${formatCurrency(p.price)}</td>
            <td>${stockBadge}</td>
            <td><span class="badge badge-info">${
              p.category || "General"
            }</span></td>
            <td><span class="badge badge-primary">${p.database}</span></td>
            <td>
              <div class="action-buttons">
                <a href="/edit-product/${p._id}" class="btn btn-warning btn-sm">
                  <i class="bi bi-pencil"></i> Editar
                </a>
                <button class="btn btn-danger btn-sm" onclick="confirmDeleteProduct('${
                  p._id
                }', '${p.name}')">
                  <i class="bi bi-trash"></i> Eliminar
                </button>
              </div>
            </td>
          </tr>
        `;
      });
    }
  } catch (err) {
    showAlert("errorGlobal", "Error al cargar productos", true);
  }
}

// Confirmar eliminación de producto
function confirmDeleteProduct(id, name) {
  if (confirm(`¿Estás seguro de eliminar el producto "${name}"?`)) {
    deleteProduct(id);
  }
}

// Eliminar producto
async function deleteProduct(id) {
  const token = localStorage.getItem("token");

  try {
    const res = await fetch(`/products/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });

    const data = await res.json();

    if (res.ok) {
      showAlert("successMessage", "Producto eliminado exitosamente");
      await loadProducts();
    } else {
      showAlert("errorGlobal", data.message, true);
    }
  } catch (err) {
    showAlert("errorGlobal", "Error al eliminar producto", true);
  }
}

// ======================
// PRODUCTOS - AGREGAR
// ======================
const productForm = document.getElementById("productForm");
if (productForm) {
  productForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("token");

    const payload = {
      name: document.getElementById("pName").value,
      price: parseFloat(document.getElementById("pPrice").value),
      stock: parseInt(document.getElementById("pStock").value),
      category: document.getElementById("pCategory").value,
      description: document.getElementById("pDesc").value,
    };

    hideAlert("productError");
    hideAlert("productMessage");

    try {
      const res = await fetch("/products", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok) {
        showAlert("productMessage", data.message);
        productForm.reset();

        // Redirigir al dashboard después de 2 segundos
        setTimeout(() => {
          window.location.href = "/dashboard";
        }, 2000);
      } else {
        showAlert("productError", data.message, true);
      }
    } catch (err) {
      showAlert("productError", "Error al crear producto", true);
    }
  });
}

// ======================
// PRODUCTOS - EDITAR
// ======================
async function loadProductForEdit() {
  const productId = document.getElementById("productId");
  if (!productId) return;

  const token = localStorage.getItem("token");
  const urlParams = new URLSearchParams(window.location.search);
  const id = window.location.pathname.split("/").pop();

  const loadingForm = document.getElementById("loadingForm");
  const editFormContainer = document.getElementById("editFormContainer");

  try {
    const res = await fetch(`/products/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    const product = await res.json();

    if (!res.ok) {
      showAlert("editError", "Producto no encontrado", true);
      return;
    }

    // Llenar el formulario
    document.getElementById("productId").value = product._id;
    document.getElementById("eName").value = product.name;
    document.getElementById("ePrice").value = product.price;
    document.getElementById("eStock").value = product.stock;
    document.getElementById("eCategory").value = product.category || "General";
    document.getElementById("eDesc").value = product.description || "";
    document.getElementById("eDatabase").value = product.database;

    // Mostrar formulario
    if (loadingForm) loadingForm.classList.add("d-none");
    if (editFormContainer) editFormContainer.classList.remove("d-none");
  } catch (err) {
    showAlert("editError", "Error al cargar producto", true);
  }
}

const editProductForm = document.getElementById("editProductForm");
if (editProductForm) {
  // Cargar datos del producto al cargar la página
  loadProductForEdit();

  editProductForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("token");
    const id = document.getElementById("productId").value;

    const payload = {
      name: document.getElementById("eName").value,
      price: parseFloat(document.getElementById("ePrice").value),
      stock: parseInt(document.getElementById("eStock").value),
      category: document.getElementById("eCategory").value,
      description: document.getElementById("eDesc").value,
    };

    hideAlert("editError");
    hideAlert("editMessage");

    try {
      const res = await fetch(`/products/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok) {
        showAlert("editMessage", "Producto actualizado exitosamente");

        // Redirigir al dashboard después de 2 segundos
        setTimeout(() => {
          window.location.href = "/dashboard";
        }, 2000);
      } else {
        showAlert("editError", data.message, true);
      }
    } catch (err) {
      showAlert("editError", "Error al actualizar producto", true);
    }
  });
}

// ======================
// USUARIOS - LISTAR
// ======================
async function loadUsers() {
  const tbody = document.getElementById("usersTable");
  if (!tbody) return;

  const token = localStorage.getItem("token");
  const loadingSpinner = document.getElementById("loadingUsersSpinner");
  const usersContainer = document.getElementById("usersContainer");
  const emptyState = document.getElementById("emptyUsersState");

  try {
    const res = await fetch("/users", {
      headers: { Authorization: `Bearer ${token}` },
    });

    const data = await res.json();

    if (!res.ok) {
      showAlert("usersError", data.message, true);
      return;
    }

    // Ocultar spinner
    if (loadingSpinner) loadingSpinner.classList.add("d-none");

    // Mostrar tabla o estado vacío
    if (data.users.length === 0) {
      if (emptyState) emptyState.classList.remove("d-none");
      if (usersContainer) usersContainer.classList.add("d-none");
    } else {
      if (emptyState) emptyState.classList.add("d-none");
      if (usersContainer) usersContainer.classList.remove("d-none");

      tbody.innerHTML = "";

      data.users.forEach((u) => {
        tbody.innerHTML += `
          <tr>
            <td><i class="bi bi-person-circle"></i> <strong>${
              u.username
            }</strong></td>
            <td><i class="bi bi-envelope"></i> ${u.email || "N/A"}</td>
            <td>${formatDate(u.created_at)}</td>
            <td>
              <button class="btn btn-danger btn-sm" onclick="confirmDeleteUser('${
                u.username
              }')">
                <i class="bi bi-trash"></i> Eliminar
              </button>
            </td>
          </tr>
        `;
      });
    }
  } catch (err) {
    showAlert("usersError", "Error al cargar usuarios", true);
  }
}

// Confirmar eliminación de usuario
function confirmDeleteUser(username) {
  if (confirm(`¿Estás seguro de eliminar al usuario "${username}"?`)) {
    deleteUser(username);
  }
}

// Eliminar usuario
async function deleteUser(username) {
  const token = localStorage.getItem("token");

  try {
    const res = await fetch(`/users/${username}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });

    const data = await res.json();

    if (res.ok) {
      showAlert("userSuccessMessage", "Usuario eliminado exitosamente");
      await loadUsers();
    } else {
      showAlert("usersError", data.message, true);
    }
  } catch (err) {
    showAlert("usersError", "Error al eliminar usuario", true);
  }
}

// ======================
// USUARIOS - REGISTRAR (Administrador)
// ======================
const adminRegisterForm = document.getElementById("adminRegisterForm");
if (adminRegisterForm) {
  adminRegisterForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("regUsername").value;
    const email = document.getElementById("regEmail").value;
    const password = document.getElementById("regPassword").value;
    const passwordConfirm = document.getElementById("regPasswordConfirm").value;

    hideAlert("registerError");
    hideAlert("registerMessage");

    // Validar que las contraseñas coincidan
    if (password !== passwordConfirm) {
      showAlert("registerError", "Las contraseñas no coinciden", true);
      return;
    }

    const token = localStorage.getItem("token");

    const payload = {
      username: username,
      email: email,
      password: password,
    };

    try {
      const res = await fetch("/users/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok) {
        showAlert("registerMessage", "Usuario registrado exitosamente");
        adminRegisterForm.reset();

        // Redirigir a usuarios después de 2 segundos
        setTimeout(() => {
          window.location.href = "/users-page";
        }, 2000);
      } else {
        showAlert(
          "registerError",
          data.message || data.error || "Error al registrar usuario",
          true
        );
      }
    } catch (err) {
      showAlert("registerError", "Error al registrar usuario", true);
    }
  });
}

// ======================
// INICIALIZACIÓN
// ======================
// Ejecutar automáticamente según la página
document.addEventListener("DOMContentLoaded", () => {
  // Cargar productos en dashboard
  if (document.getElementById("productsTable")) {
    loadProducts();
  }

  // Cargar usuarios en página de usuarios
  if (document.getElementById("usersTable")) {
    loadUsers();
  }
});
