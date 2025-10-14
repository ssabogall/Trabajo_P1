// ======== POS simple: estado del carrito =========
const orderList   = document.getElementById("order-list");
const orderTotal  = document.getElementById("order-total");
const checkoutBtn = document.getElementById("checkout-btn");

// Inputs cliente
const cedulaInput = document.getElementById("cedula");
const nombreInput = document.getElementById("nombre");     // <- importante
const correoInput = document.getElementById("correo");

// Toggle de pago (opcional)
let paymentMethod = "Cash";
const paymentToggle = document.getElementById("payment-toggle");
if (paymentToggle) {
  paymentToggle.addEventListener("click", () => {
    paymentMethod = paymentMethod === "Cash" ? "Card" : "Cash";
    paymentToggle.textContent = paymentMethod;
  });
}

// Carrito en memoria: [{id, name, unit, qty}]
let cart = [];

// -------- helpers --------
function renderCart() {
  orderList.innerHTML = "";
  let total = 0;

  cart.forEach((it, idx) => {
    const li = document.createElement("li");
    li.className = "list-group-item d-flex justify-content-between align-items-center";

    const left = document.createElement("div");
    left.innerHTML = `<strong>${it.name}</strong><br><small>x${it.qty}</small>`;

    const right = document.createElement("div");
    right.innerHTML = `$${(Number(it.unit) * it.qty).toFixed(2)} `;

    const minus = document.createElement("button");
    minus.className = "btn btn-sm btn-outline-secondary ms-2";
    minus.textContent = "-";
    minus.onclick = () => {
      it.qty -= 1;
      if (it.qty <= 0) cart.splice(idx, 1);
      renderCart();
    };

    const remove = document.createElement("button");
    remove.className = "btn btn-sm btn-outline-danger ms-2";
    remove.textContent = "×";
    remove.onclick = () => {
      cart.splice(idx, 1);
      renderCart();
    };

    right.appendChild(minus);
    right.appendChild(remove);
    li.appendChild(left);
    li.appendChild(right);
    orderList.appendChild(li);

    total += Number(it.unit) * it.qty;
  });

  orderTotal.textContent = total.toFixed(2);
  checkoutBtn.disabled = cart.length === 0;
}

function addToCart(id, name, price) {
  id = Number(id);
  price = Number(price);

  const found = cart.find(x => x.id === id);
  if (found) found.qty += 1;
  else cart.push({ id, name, unit: price, qty: 1 });
  renderCart();
}

// -------- botones "Add" de cada producto --------
document.querySelectorAll(".add-to-order-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const id    = btn.dataset.id;
    const name  = btn.dataset.name;
    const price = btn.dataset.price;
    addToCart(id, name, price);
  });
});

// -------- CSRF --------
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");

// -------- Checkout --------
checkoutBtn.addEventListener("click", async () => {
  const cedula = (cedulaInput?.value || "").trim();
  const nombre = (nombreInput?.value || "").trim();  // <- se envía 'nombre'
  const correo = (correoInput?.value || "").trim();

  const payload = {
    paymentMethod,
    customer: { cedula, nombre, correo },
    orders: cart.map(it => ({ id: it.id, quantity: it.qty })),
  };

  try {
    const resp = await fetch("/save_order/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken
      },
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    if (!resp.ok || data.status !== "success") {
      alert(data.message || "No se pudo guardar la orden");
      return;
    }

    // Éxito: limpiar carrito e inputs
    cart = [];
    renderCart();
    cedulaInput.value = "";
    nombreInput.value = "";
    correoInput.value = "";
    alert(`Orden #${data.order_id} creada. Total: $${data.totals.total}`);
    // Redirige si quieres:
    // location.href = "/pos/orders";
  } catch (e) {
    console.error(e);
    alert("Error de red");
  }
});

// Inicial
renderCart();
