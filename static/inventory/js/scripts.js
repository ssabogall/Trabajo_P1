/*!
* Start Bootstrap - Bare v5.0.9 (https://startbootstrap.com/template/bare)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-bare/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project

// Carrito de compras
let cart = [];

// Elementos del DOM
const cartIcon = document.getElementById('cart-icon');
const cartDropdown = document.getElementById('cart-dropdown');
const cartClose = document.getElementById('cart-close');
const cartBadge = document.getElementById('cart-badge');
const cartBody = document.getElementById('cart-body');
const cartEmpty = document.getElementById('cart-empty');
const cartFooter = document.getElementById('cart-footer');
const cartTotal = document.getElementById('cart-total');
const clearCartBtn = document.getElementById('clear-cart');
const checkoutCartBtn = document.getElementById('checkout-cart');
const addToCartBtns = document.querySelectorAll('.add-to-cart-btn');

// Toggle carrito
cartIcon.addEventListener('click', (e) => {
    e.stopPropagation();
    cartDropdown.classList.toggle('show');
});

cartClose.addEventListener('click', () => {
    cartDropdown.classList.remove('show');
});

//  Evitar que el carrito se cierre al hacer click dentro
cartDropdown.addEventListener('click', (e) => {
    e.stopPropagation();
});

// Cerrar carrito al hacer click fuera
document.addEventListener('click', (e) => {
    if (!cartIcon.contains(e.target) && !cartDropdown.contains(e.target)) {
        cartDropdown.classList.remove('show');
    }
});

// Agregar al carrito
addToCartBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.stopPropagation();

        const productId = btn.dataset.id;
        const productName = btn.dataset.name;
        const productPrice = parseFloat(btn.dataset.price);

        addToCart(productId, productName, productPrice);
        
        // Animación del botón
        btn.innerHTML = '<i class="fas fa-check me-1"></i>Agregado';
        btn.classList.add('btn-success');
        btn.classList.remove('btn-outline-dark');
        
        setTimeout(() => {
            btn.innerHTML = '<i class="fas fa-cart-plus me-1"></i>Agregar';
            btn.classList.remove('btn-success');
            btn.classList.add('btn-outline-dark');
        }, 1000);
    });
});

// Función para agregar al carrito
function addToCart(id, name, price) {
    const existingItem = cart.find(item => item.id === id);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: id,
            name: name,
            price: price,
            quantity: 1
        });
    }
    
    updateCartDisplay();
}

// Función para remover del carrito
function removeFromCart(id) {
    cart = cart.filter(item => item.id !== id);
    updateCartDisplay();
}

// Función para actualizar cantidad
function updateQuantity(id, change) {
    const item = cart.find(item => item.id === id);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(id);
        } else {
            updateCartDisplay();
        }
    }
}

// Función para limpiar carrito
function clearCart() {
    cart = [];
    updateCartDisplay();
}

// Función para actualizar la visualización del carrito
function updateCartDisplay() {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const totalPrice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    // Actualizar badge
    cartBadge.textContent = totalItems;
    cartBadge.style.display = totalItems > 0 ? 'flex' : 'none';

    // Actualizar total
    cartTotal.textContent = totalPrice.toFixed(2);

    // Mostrar/ocultar elementos según si hay items
    if (cart.length === 0) {
        cartEmpty.style.display = 'block';
        cartFooter.style.display = 'none';
        cartBody.innerHTML = `
            <div class="cart-empty" id="cart-empty">
                <i class="fa-solid fa-bread-slice"></i>
                <p>Tu carrito está vacío</p>
            </div>
        `;
    } else {
        cartEmpty.style.display = 'none';
        cartFooter.style.display = 'block';
        
        // Generar HTML de items
        cartBody.innerHTML = cart.map(item => `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">$${item.price.toFixed(2)} c/u</div>
                </div>
                <div class="cart-item-controls">
                    <div class="quantity-controls">
                        <button class="quantity-btn" onclick="updateQuantity('${item.id}', -1)">-</button>
                        <span class="quantity-display">${item.quantity}</span>
                        <button class="quantity-btn" onclick="updateQuantity('${item.id}', 1)">+</button>
                    </div>
                    <i class="fas fa-trash remove-item" onclick="removeFromCart('${item.id}')"></i>
                </div>
            </div>
        `).join('');
    }


    cartDropdown.classList.add('show');
}

// Checkout
checkoutCartBtn.addEventListener('click', async () => {
    let cartString = encodeURIComponent(JSON.stringify(cart));
    localStorage.setItem("cart", JSON.stringify(cart));
    window.location.href = "forms";
});

// Inicializar carrito vacío
updateCartDisplay();