let cart = JSON.parse(localStorage.getItem("cart")) || [];


console.log("Cart loaded on form page:", cart);

const checkoutCartBtn = document.getElementById('checkout'); 
const firstNameInput = document.getElementById('firstName');
const lastNameInput = document.getElementById('lastName');
const cedulaInput = document.getElementById('cedula');
const phoneInput = document.getElementById('phone');
const addressInput = document.getElementById('address');
const cityInput = document.getElementById('city');
const neighborhoodInput = document.getElementById('neighborhood');

checkoutCartBtn.addEventListener('click', async () => {
  console.log(firstNameInput);
  console.log("success");
      const customer = {
        firstName: firstNameInput.value.trim(),
        lastName: lastNameInput.value.trim(),
        cedula: cedulaInput.value.trim(),
        phone: phoneInput.value.trim(),
        address: addressInput.value.trim(),
        city: cityInput.value.trim(),
        neighborhood: neighborhoodInput.value.trim(),
    };
  

        // Aquí puedes agregar la lógica para proceder al checkout
        alert(`Procesando compra por $${cart.reduce((sum, item) => sum + (item.price * item.quantity), 0).toFixed(2)}`);
        console.log('Cart items:', cart);
        
        const ordersToSend = cart.map(cart => ({
            ...cart,
              customer,
        }));
                    
        console.log('Sending orders:', ordersToSend);

        
        const response = await fetch('/save_order_online/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ orders: ordersToSend })
        });
        
        
        const data = await response.json();
        console.log('Pedido guardado', data);

});