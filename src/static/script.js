// Global variables
let currentUser = null;
let isAuthenticated = false;

// API Base URL
const API_BASE = '/api';

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

// Initialize application
async function initializeApp() {
    try {
        showLoading();
        await checkAuthStatus();
        hideLoading();
    } catch (error) {
        console.error('Error initializing app:', error);
        hideLoading();
    }
}

// Setup event listeners
function setupEventListeners() {
    // Mobile menu toggle
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }

    // User type change in register form
    const userTypeSelect = document.getElementById('register-user-type');
    const brandNameGroup = document.getElementById('brand-name-group');
    
    if (userTypeSelect && brandNameGroup) {
        userTypeSelect.addEventListener('change', (e) => {
            if (e.target.value === 'brand_admin') {
                brandNameGroup.style.display = 'block';
                document.getElementById('register-brand-name').required = true;
            } else {
                brandNameGroup.style.display = 'none';
                document.getElementById('register-brand-name').required = false;
            }
        });
    }

    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });

    // Auto-dismiss toasts
    setInterval(cleanupToasts, 5000);
}

// Authentication functions
async function checkAuthStatus() {
    try {
        const response = await fetch(`${API_BASE}/auth/check-auth`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.authenticated) {
                isAuthenticated = true;
                await getCurrentUser();
                showDashboard();
            } else {
                showLandingPage();
            }
        } else {
            showLandingPage();
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
        showLandingPage();
    }
}

async function getCurrentUser() {
    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            updateNavigation();
        }
    } catch (error) {
        console.error('Error getting current user:', error);
    }
}

async function login(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            isAuthenticated = true;
            closeModal('login-modal');
            showToast('¡Bienvenido de vuelta!', 'success');
            showDashboard();
            updateNavigation();
        } else {
            showToast(data.error || 'Error al iniciar sesión', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Error de conexión', 'error');
    } finally {
        hideLoading();
    }
}

async function register(event) {
    event.preventDefault();
    
    const formData = {
        nombre: document.getElementById('register-name').value,
        email: document.getElementById('register-email').value,
        password: document.getElementById('register-password').value,
        user_type: document.getElementById('register-user-type').value
    };
    
    if (formData.user_type === 'brand_admin') {
        formData.marca_nombre = document.getElementById('register-brand-name').value;
    }
    
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            isAuthenticated = true;
            closeModal('register-modal');
            showToast('¡Registro exitoso! Bienvenido a Weev', 'success');
            showDashboard();
            updateNavigation();
        } else {
            showToast(data.error || 'Error al registrarse', 'error');
        }
    } catch (error) {
        console.error('Register error:', error);
        showToast('Error de conexión', 'error');
    } finally {
        hideLoading();
    }
}

async function logout() {
    try {
        const response = await fetch(`${API_BASE}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            currentUser = null;
            isAuthenticated = false;
            showToast('Sesión cerrada correctamente', 'success');
            showLandingPage();
            updateNavigation();
        }
    } catch (error) {
        console.error('Logout error:', error);
        showToast('Error al cerrar sesión', 'error');
    }
}

// Product activation
async function activateProduct() {
    const code = document.getElementById('activation-code').value.trim().toUpperCase();
    const resultDiv = document.getElementById('activation-result');
    
    if (!code) {
        showToast('Por favor ingresa un código de activación', 'warning');
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/activate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ codigo_activacion: code })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.className = 'activation-result success';
            resultDiv.innerHTML = `
                <h4>¡Producto activado exitosamente!</h4>
                <p><strong>Producto:</strong> ${data.activacion.producto.nombre}</p>
                <p><strong>Puntos ganados:</strong> ${data.puntos_ganados}</p>
                <p><strong>Puntos totales:</strong> ${data.puntos_totales}</p>
                <p><strong>Nivel actual:</strong> ${data.nivel_actual}</p>
                ${data.recompensas_otorgadas.length > 0 ? 
                    `<p><strong>Recompensas obtenidas:</strong> ${data.recompensas_otorgadas.length}</p>` : 
                    ''
                }
            `;
            resultDiv.style.display = 'block';
            
            document.getElementById('activation-code').value = '';
            showToast('¡Producto activado! Revisa tus recompensas', 'success');
            
            // Refresh dashboard data
            if (currentUser.user_type === 'consumer') {
                loadUserDashboard();
            }
        } else {
            resultDiv.className = 'activation-result error';
            resultDiv.innerHTML = `<p>${data.error}</p>`;
            resultDiv.style.display = 'block';
            showToast(data.error, 'error');
        }
    } catch (error) {
        console.error('Activation error:', error);
        resultDiv.className = 'activation-result error';
        resultDiv.innerHTML = '<p>Error de conexión. Inténtalo de nuevo.</p>';
        resultDiv.style.display = 'block';
        showToast('Error de conexión', 'error');
    } finally {
        hideLoading();
    }
}

// Product management
async function createProduct(event) {
    event.preventDefault();
    
    const formData = {
        nombre: document.getElementById('product-name').value,
        descripcion: document.getElementById('product-description').value,
        categoria: document.getElementById('product-category').value,
        precio: parseFloat(document.getElementById('product-price').value) || null,
        imagen_url: document.getElementById('product-image').value || null
    };
    
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            closeModal('create-product-modal');
            showToast('Producto creado exitosamente', 'success');
            document.getElementById('create-product-form').reset();
            
            // Refresh brand dashboard
            if (currentUser.user_type === 'brand_admin') {
                loadBrandDashboard();
            }
        } else {
            showToast(data.error || 'Error al crear producto', 'error');
        }
    } catch (error) {
        console.error('Create product error:', error);
        showToast('Error de conexión', 'error');
    } finally {
        hideLoading();
    }
}

// Dashboard functions
async function loadUserDashboard() {
    try {
        const response = await fetch(`${API_BASE}/user-dashboard`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            updateUserDashboard(data);
        }
    } catch (error) {
        console.error('Error loading user dashboard:', error);
    }
}

async function loadBrandDashboard() {
    try {
        const response = await fetch(`${API_BASE}/brand-dashboard`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            updateBrandDashboard(data);
        }
    } catch (error) {
        console.error('Error loading brand dashboard:', error);
    }
}

function updateUserDashboard(data) {
    // Update stats
    document.getElementById('user-points').textContent = data.metricas.puntos_totales;
    document.getElementById('user-level').textContent = data.metricas.nivel_actual;
    document.getElementById('user-activations').textContent = data.metricas.total_activaciones;
    
    // Update recent activations
    const activationsList = document.getElementById('recent-activations');
    if (data.activaciones_recientes.length === 0) {
        activationsList.innerHTML = '<p>No tienes activaciones recientes.</p>';
    } else {
        activationsList.innerHTML = data.activaciones_recientes.map(activation => `
            <div class="activation-item">
                <div class="item-info">
                    <h4>${activation.producto.nombre}</h4>
                    <p>Marca: ${activation.producto.marca} • Puntos: ${activation.puntos_ganados}</p>
                </div>
                <div class="item-meta">
                    ${new Date(activation.fecha_activacion).toLocaleDateString()}
                </div>
            </div>
        `).join('');
    }
    
    // Update available rewards
    loadUserRewards();
}

function updateBrandDashboard(data) {
    // Update stats
    const statsContainer = document.getElementById('brand-stats');
    statsContainer.innerHTML = `
        <div class="stat-card">
            <div class="stat-number">${data.metricas.total_productos}</div>
            <div class="stat-label">Productos</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${data.metricas.productos_activos}</div>
            <div class="stat-label">Activos</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${data.metricas.total_activaciones}</div>
            <div class="stat-label">Activaciones</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${data.metricas.usuarios_unicos}</div>
            <div class="stat-label">Usuarios</div>
        </div>
    `;
    
    // Update products list
    const productsList = document.getElementById('brand-products');
    if (data.productos_top.length === 0) {
        productsList.innerHTML = '<p>No tienes productos creados.</p>';
    } else {
        productsList.innerHTML = data.productos_top.map(product => `
            <div class="product-item">
                <div class="item-info">
                    <h4>${product.nombre}</h4>
                    <p>Activaciones: ${product.activaciones}</p>
                </div>
                <div class="item-actions">
                    <button class="btn btn-outline" onclick="editProduct(${product.id})">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    // Update recent activations
    const activationsList = document.getElementById('brand-activations');
    if (data.activaciones_recientes.length === 0) {
        activationsList.innerHTML = '<p>No hay activaciones recientes.</p>';
    } else {
        activationsList.innerHTML = data.activaciones_recientes.map(activation => `
            <div class="activation-item">
                <div class="item-info">
                    <h4>${activation.producto_nombre}</h4>
                    <p>Usuario: ${activation.usuario_nombre} • Puntos: ${activation.puntos_ganados}</p>
                </div>
                <div class="item-meta">
                    ${new Date(activation.fecha_activacion).toLocaleDateString()}
                </div>
            </div>
        `).join('');
    }
}

async function loadUserRewards() {
    try {
        const response = await fetch(`${API_BASE}/my-rewards?estado=disponible`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const rewardsList = document.getElementById('available-rewards');
            
            if (data.recompensas.length === 0) {
                rewardsList.innerHTML = '<p>No tienes recompensas disponibles.</p>';
            } else {
                rewardsList.innerHTML = data.recompensas.map(userReward => `
                    <div class="reward-item">
                        <div class="item-info">
                            <h4>${userReward.recompensa.nombre}</h4>
                            <p>${userReward.recompensa.descripcion}</p>
                            <p><strong>Valor:</strong> ${userReward.recompensa.valor}</p>
                        </div>
                        <div class="item-actions">
                            <button class="btn btn-success" onclick="claimReward(${userReward.id})">
                                <i class="fas fa-gift"></i> Reclamar
                            </button>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Error loading user rewards:', error);
    }
}

async function claimReward(userRewardId) {
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/claim/${userRewardId}`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('¡Recompensa reclamada exitosamente!', 'success');
            loadUserRewards(); // Refresh rewards list
            loadUserDashboard(); // Refresh dashboard stats
        } else {
            showToast(data.error || 'Error al reclamar recompensa', 'error');
        }
    } catch (error) {
        console.error('Claim reward error:', error);
        showToast('Error de conexión', 'error');
    } finally {
        hideLoading();
    }
}

// UI functions
function showLandingPage() {
    document.getElementById('landing-page').style.display = 'block';
    document.getElementById('dashboard-section').style.display = 'none';
}

function showDashboard() {
    document.getElementById('landing-page').style.display = 'none';
    document.getElementById('dashboard-section').style.display = 'block';
    
    if (currentUser) {
        if (currentUser.user_type === 'consumer') {
            document.getElementById('consumer-dashboard').style.display = 'block';
            document.getElementById('brand-dashboard').style.display = 'none';
            loadUserDashboard();
        } else if (currentUser.user_type === 'brand_admin') {
            document.getElementById('consumer-dashboard').style.display = 'none';
            document.getElementById('brand-dashboard').style.display = 'block';
            loadBrandDashboard();
        }
    }
}

function updateNavigation() {
    const navAuth = document.getElementById('nav-auth');
    const navUser = document.getElementById('nav-user');
    const userName = document.getElementById('user-name');
    
    if (isAuthenticated && currentUser) {
        navAuth.style.display = 'none';
        navUser.style.display = 'flex';
        userName.textContent = currentUser.nombre;
    } else {
        navAuth.style.display = 'flex';
        navUser.style.display = 'none';
    }
}

function showModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function showLoginModal() {
    showModal('login-modal');
}

function showRegisterModal() {
    showModal('register-modal');
}

function showCreateProductModal() {
    showModal('create-product-modal');
}

function showCreateRewardModal() {
    // TODO: Implement create reward modal
    showToast('Funcionalidad en desarrollo', 'warning');
}

function editProduct(productId) {
    // TODO: Implement edit product functionality
    showToast('Funcionalidad en desarrollo', 'warning');
}

function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

function getToastIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

function cleanupToasts() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        if (toast.offsetParent === null) { // Hidden toast
            toast.remove();
        }
    });
}

function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// Utility functions
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

