// scriptProducts.js
(function () {
  // ---------- Helpers ----------
  const money = (n) => '$' + Number(n || 0).toLocaleString('es-CO');

  // Estado del carrito
  let cart = [];

  // Nodos que usamos
  const listEl   = document.getElementById('mini-cart-items');
  const totalEl  = document.getElementById('mini-cart-total');
  const countEl  = document.getElementById('mini-cart-count');
  const clearBtn = document.getElementById('cart-clear');
  const buyBtn   = document.getElementById('cart-buy');

  const form     = document.getElementById('cart-form');
  const ordersIn = document.getElementById('cart-orders');
  const cedIn    = document.getElementById('cart-cedula');   // opcionales
  const nomIn    = document.getElementById('cart-nombre');
  const mailIn   = document.getElementById('cart-correo');

  // ---------- Persistencia local ----------
  function load() {
    try {
      cart = JSON.parse(localStorage.getItem('baneton_cart') || '[]');
    } catch (_) { cart = []; }
  }
  function save() {
    localStorage.setItem('baneton_cart', JSON.stringify(cart));
  }

  // ---------- Render del mini-carrito ----------
  function render() {
    if (!listEl) return;

    listEl.innerHTML = '';
    let total = 0;

    cart.forEach(item => {
      const li = document.createElement('li');
      li.className = 'list-group-item d-flex justify-content-between align-items-center';

      const left = document.createElement('div');
      left.innerHTML = `
        <div class="fw-semibold">${item.name}</div>
        <small>${money(item.price)} c/u</small>
      `;

      const right = document.createElement('div');
      right.className = 'd-flex align-items-center gap-1';
      right.innerHTML = `
        <button class="btn btn-sm btn-outline-secondary js-dec" aria-label="Restar">–</button>
        <span class="mx-1">${item.qty}</span>
        <button class="btn btn-sm btn-outline-secondary js-inc" aria-label="Sumar">+</button>
        <button class="btn btn-sm btn-outline-danger ms-2 js-del" aria-label="Quitar">🗑</button>
        <span class="ms-2">${money(item.price * item.qty)}</span>
      `;

      // Eventos de línea
      right.querySelector('.js-inc').addEventListener('click', () => { item.qty++; save(); render(); });
      right.querySelector('.js-dec').addEventListener('click', () => {
        item.qty = Math.max(1, item.qty - 1);
        save(); render();
      });
      right.querySelector('.js-del').addEventListener('click', () => {
        cart = cart.filter(x => x.id !== item.id);
        save(); render();
      });

      li.appendChild(left);
      li.appendChild(right);
      listEl.appendChild(li);

      total += item.price * item.qty;
    });

    if (totalEl) totalEl.textContent = money(total);
    if (countEl) countEl.textContent = String(cart.reduce((a, b) => a + b.qty, 0));
  }

  // ---------- API de carrito ----------
  function addItem({ id, name, price }) {
    id = Number(id); price = Number(price);
    if (!id || !name || !price) return;

    const found = cart.find(x => x.id === id);
    if (found) found.qty += 1;
    else cart.push({ id, name, price, qty: 1 });

    save(); render();
  }

  // ---------- Delegación: click en botones Agregar ----------
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.product-add');
    if (!btn) return;

    const id    = btn.dataset.id || btn.getAttribute('data-id');
    const name  = btn.dataset.name || btn.getAttribute('data-name') || btn.textContent.trim();
    const price = btn.dataset.price || btn.getAttribute('data-price');

    addItem({ id, name, price });
  });

  // ---------- Limpiar ----------
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      cart = [];
      save(); render();
    });
  }

  // ---------- Comprar (POST normal con form oculto) ----------
  if (buyBtn && form && ordersIn) {
    buyBtn.addEventListener('click', () => {
      if (cart.length === 0) return;

      // Si tienes inputs visibles para cédula/nombre/correo en la página,
      // cópialos a los hidden aquí. (Quita si no usas cliente en products)
      const ced = document.querySelector('[data-customer="cedula"]');
      const nom = document.querySelector('[data-customer="nombre"]');
      const mail = document.querySelector('[data-customer="correo"]');
      if (cedIn && ced)  cedIn.value  = ced.value || '';
      if (nomIn && nom)  nomIn.value  = nom.value || '';
      if (mailIn && mail) mailIn.value = mail.value || '';

      const payload = cart.map(i => ({ id: i.id, quantity: i.qty }));
      ordersIn.value = JSON.stringify(payload);

      form.submit(); // Django maneja CSRF y redirect
    });
  }

  // Init
  load(); render();
})();
