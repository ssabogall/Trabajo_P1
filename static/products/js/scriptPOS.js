// =========================
// POS SCRIPT - CLEAN VERSION
// =========================

// --- Load existing cart ---
let cart = JSON.parse(localStorage.getItem("cart")) || [];
console.log("Cart loaded:", cart);

// --- Element references ---
const orderList = document.getElementById('order-list');
const orderTotalEl = document.getElementById('order-total');
const checkoutBtn = document.getElementById('checkout-btn');
const paymentToggle = document.getElementById('payment-toggle');

// Customer fields
const cedulaInput = document.getElementById('cedula');
const nombreInput = document.getElementById('nombre');
const correoInput = document.getElementById('correo');

// --- Payment method ---
let paymentMethod = 'Cash';

// =========================
// CART FUNCTIONS
// =========================
function saveCart() {
    localStorage.setItem("cart", JSON.stringify(cart));
}

function updateCartDisplay() {
    orderList.innerHTML = '';

    if (cart.length === 0) {
        orderList.innerHTML = `
            <li class="list-group-item text-center text-muted py-4">
                <em>No products added</em>
            </li>`;
        orderTotalEl.textContent = '0.00';
        checkoutBtn.disabled = true;
        return;
    }

    let total = 0;

    cart.forEach((item, index) => {
        total += item.price * item.quantity;

        const li = document.createElement('li');
        li.className = 'list-group-item cart-item d-flex justify-content-between align-items-center mb-2';
        li.innerHTML = `
            <div class="cart-info">
                <strong class="cart-name">${item.name}</strong>
                <small class="text-muted d-block">x${item.quantity} • $${item.price.toFixed(2)} each</small>
            </div>
            <div class="cart-actions btn-group" role="group">
                <button class="btn btn-sm btn-outline-secondary" data-action="decrease" data-index="${index}">−</button>
                <span class="mx-2 fw-bold">${item.quantity}</span>
                <button class="btn btn-sm btn-outline-secondary" data-action="increase" data-index="${index}">＋</button>
                <button class="btn btn-sm btn-outline-danger ms-2" data-action="remove" data-index="${index}">🗑</button>
            </div>
        `;
        li.style.animation = 'fadeIn 0.3s ease';
        orderList.appendChild(li);
    });

    orderTotalEl.textContent = total.toFixed(2);
    checkoutBtn.disabled = false;
    saveCart();
}

// =========================
// ADD TO CART BUTTONS
// =========================
document.querySelectorAll('.add-to-order-btn').forEach(button => {
    button.addEventListener('click', () => {
        const productId = button.dataset.id;
        const name = button.dataset.name;
        const price = parseFloat(button.dataset.price);

        const existing = cart.find(item => item.id === productId);
        if (existing) {
            existing.quantity += 1;
        } else {
            cart.push({ id: productId, name, price, quantity: 1 });
        }

        updateCartDisplay();
        showAlert(`${name} added to order`, 'success');
    });
});

// =========================
// CART ITEM BUTTON HANDLERS
// =========================
orderList.addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;

    const index = btn.dataset.index;
    const action = btn.dataset.action;

    if (action === 'increase') {
        cart[index].quantity += 1;
    } else if (action === 'decrease') {
        cart[index].quantity -= 1;
        if (cart[index].quantity <= 0) cart.splice(index, 1);
    } else if (action === 'remove') {
        cart.splice(index, 1);
    }

    updateCartDisplay();
});

// =========================
// PAYMENT TOGGLE
// =========================
paymentToggle.addEventListener('click', () => {
    if (paymentMethod === 'Cash') {
        paymentMethod = 'Card';
        paymentToggle.textContent = 'Card';
        paymentToggle.classList.remove('btn-outline-primary');
        paymentToggle.classList.add('btn-primary');
    } else {
        paymentMethod = 'Cash';
        paymentToggle.textContent = 'Cash';
        paymentToggle.classList.remove('btn-primary');
        paymentToggle.classList.add('btn-outline-primary');
    }
});

// =========================
// CHECKOUT
// =========================
checkoutBtn.addEventListener('click', async () => {
    if (cart.length === 0) {
        showAlert('Cart is empty', 'danger');
        return;
    }

    if (
        cedulaInput.value.trim() === '' ||
        nombreInput.value.trim() === '' ||
        correoInput.value.trim() === ''
    ) {
        showAlert('Please fill in all customer fields', 'warning');
        return;
    }

    const customer = {
        cedula: cedulaInput.value.trim(),
        nombre: nombreInput.value.trim(),
        correo: correoInput.value.trim(),
    };

    const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

    const payload = {
        orders: cart,
        customer,
        paymentMethod,
        total
    };

    console.log('Sending order:', payload);

    try {
        const response = await fetch('/save_order/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const data = await response.json();
        console.log('Order saved:', data);

        showAlert('Order saved successfully!', 'success');
        cart = [];
        saveCart();
        updateCartDisplay();
        cedulaInput.value = '';
        nombreInput.value = '';
        correoInput.value = '';

    } catch (error) {
        console.error('Error saving order:', error);
        showAlert('Error saving order. Try again.', 'danger');
    }
});

// =========================
// ALERTS
// =========================
function showAlert(message, type = 'info') {
    const container = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    container.appendChild(alert);

    setTimeout(() => {
        alert.classList.remove('show');
        alert.classList.add('hide');
        setTimeout(() => alert.remove(), 400);
    }, 3000);
}


updateCartDisplay();
