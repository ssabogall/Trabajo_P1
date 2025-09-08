const orderList = document.getElementById('order-list');
const orderTotal = document.getElementById('order-total');
const checkoutBtn = document.getElementById('checkout-btn');
const paymentToggleBtn = document.getElementById('payment-toggle');

let total = 0;
let orders = [];
let isTransfer = false;

function updateTotal() {
    orderTotal.textContent = total.toFixed(2);
    checkoutBtn.disabled = orders.length === 0;
}

// Add product to order
document.querySelectorAll('.add-to-order-btn').forEach(button => {
    button.addEventListener('click', () => {
        const id = button.getAttribute('data-id');
        const name = button.getAttribute('data-name');
        const price = parseFloat(button.getAttribute('data-price'));

        orders.push({ id, name, price });
        total += price;

        const li = document.createElement('li');
        li.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');

        const itemName = document.createElement('span');
        itemName.textContent = name;

        const priceSpan = document.createElement('span');
        priceSpan.textContent = `$${price.toFixed(2)}`;
        priceSpan.classList.add('ms-2');

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = '×';
        deleteBtn.classList.add('btn', 'btn-sm', 'btn-danger', 'ms-3');
        deleteBtn.addEventListener('click', () => {
            const index = orders.findIndex(o => o.name === name && o.price === price);
            if (index > -1) {
                orders.splice(index, 1);
                total -= price;
            }
            li.remove();
            updateTotal();
        });

        const rightSide = document.createElement('div');
        rightSide.classList.add('d-flex', 'align-items-center');
        rightSide.appendChild(priceSpan);
        rightSide.appendChild(deleteBtn);

        li.appendChild(itemName);
        li.appendChild(rightSide);

        orderList.appendChild(li);

        updateTotal();
    });
});

// Payment toggle
paymentToggleBtn.addEventListener('click', () => {
    isTransfer = !isTransfer;
    paymentToggleBtn.textContent = isTransfer ? 'Transfer' : 'Cash';
    paymentToggleBtn.classList.toggle('btn-primary', isTransfer);
    paymentToggleBtn.classList.toggle('btn-outline-primary', !isTransfer);
});


// Checkout
checkoutBtn.addEventListener('click', async () => {
    const cedula = document.getElementById("cedula").value;
    const nombre = document.getElementById("nombre").value;
    const correo = document.getElementById("correo").value;
    const customer = {
        cedula: cedula.value.trim(),
        nombre: nombre.value.trim(),
        correo:correo.value.trim(),
    };


    const ordersToSend = orders.map(order => ({
        ...order,
        paymentMethod: isTransfer ? "Transfer" : "Cash",

    }));
    console.log(ordersToSend);
    
    const response = await fetch('/save_order_online/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ orders: ordersToSend, customer:customer })
    });
    
    console.log(total)
    console.log(ordersToSend)
    const data = await response.json();
    console.log('Pedido guardado', data);
});
