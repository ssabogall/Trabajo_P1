
let cart = JSON.parse(localStorage.getItem("cart")) || [];
console.log("Cart loaded on form page:", cart);

const form = document.getElementById('customerForm');

const firstNameInput = document.getElementById('firstName');
const lastNameInput = document.getElementById('lastName');
const cedulaInput = document.getElementById('cedula');
const phoneInput = document.getElementById('phone');
const addressInput = document.getElementById('address');
const cityInput = document.getElementById('city');
const neighborhoodInput = document.getElementById('neighborhood');


// Show error message below input
function showError(input, message) {
    input.classList.add('is-invalid');
    let errorDiv = input.parentElement.querySelector('.invalid-feedback');

    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        input.parentElement.appendChild(errorDiv);
    }

    errorDiv.textContent = message;
}

// Clear error message
function clearError(input) {
    input.classList.remove('is-invalid');
    const errorDiv = input.parentElement.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.textContent = '';
    }
}

// Enforce max length (30)
function enforceMaxLength(input, maxLength = 30) {
    input.addEventListener('input', () => {
        if (input.value.length > maxLength) {
            input.value = input.value.slice(0, maxLength); // Trim extra chars
            showError(input, `Máximo ${maxLength} caracteres permitidos.`);
        } else {
            clearError(input);
        }
    });
}

// Enforce numeric only for cedula (ID)
function enforceNumeric(input) {
    input.addEventListener('input', () => {
        input.value = input.value.replace(/\D/g, '');
    });
}


[
    firstNameInput,
    lastNameInput,
    cedulaInput,
    phoneInput,
    addressInput,
    cityInput,
    neighborhoodInput
].forEach(input => enforceMaxLength(input, 30));

enforceNumeric(cedulaInput);


form.addEventListener('submit', async (e) => {
    e.preventDefault(); // Stop normal form submission

    let valid = true;

    // First Name
    if (firstNameInput.value.trim() === '') {
        showError(firstNameInput, 'Este campo es obligatorio.');
        valid = false;
    } else {
        clearError(firstNameInput);
    }

    // Last Name
    if (lastNameInput.value.trim() === '') {
        showError(lastNameInput, 'Este campo es obligatorio.');
        valid = false;
    } else {
        clearError(lastNameInput);
    }

    // Cedula (ID)
    if (cedulaInput.value.trim() === '') {
        showError(cedulaInput, 'El ID es obligatorio.');
        valid = false;
    } else if (!/^\d+$/.test(cedulaInput.value.trim())) {
        showError(cedulaInput, 'Solo se permiten números en el ID.');
        valid = false;
    } else {
        clearError(cedulaInput);
    }

    // Phone (now mandatory)
    if (phoneInput.value.trim() === '') {
        showError(phoneInput, 'El número de celular es obligatorio.');
        valid = false;
    } else {
        // Optional: basic phone validation
        const phoneValue = phoneInput.value.trim();
        const phoneRegex = /^\+?\d{7,15}$/;
        if (!phoneRegex.test(phoneValue)) {
            showError(phoneInput, 'Número de celular no válido.');
            valid = false;
        } else {
            clearError(phoneInput);
        }
    }

    // Address
    if (addressInput.value.trim() === '') {
        showError(addressInput, 'La dirección es obligatoria.');
        valid = false;
    } else {
        clearError(addressInput);
    }

    // City
    if (cityInput.value.trim() === '') {
        showError(cityInput, 'La ciudad es obligatoria.');
        valid = false;
    } else {
        clearError(cityInput);
    }

    // Neighborhood
    if (neighborhoodInput.value.trim() === '') {
        showError(neighborhoodInput, 'El barrio es obligatorio.');
        valid = false;
    } else {
        clearError(neighborhoodInput);
    }

    if (!valid) {
        // Focus first invalid field
        const firstInvalid = form.querySelector('.is-invalid');
        if (firstInvalid) firstInvalid.focus();
        return;
    }

    const customer = {
        firstName: firstNameInput.value.trim(),
        lastName: lastNameInput.value.trim(),
        cedula: cedulaInput.value.trim(),
        phone: phoneInput.value.trim(),
        address: addressInput.value.trim(),
        city: cityInput.value.trim(),
        neighborhood: neighborhoodInput.value.trim(),
    };


    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    alert(`Procesando compra por $${total.toFixed(2)}`);
    console.log('Cart items:', cart);


    try {
        const response = await fetch('/save_order_online/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ orders: cart, customer }),
        });

        const data = await response.json();
        console.log('Pedido guardado', data);

        // Clear cart after successful order
        localStorage.removeItem('cart');
        alert('Pedido guardado exitosamente ');
        form.reset();

    } catch (error) {
        console.error('Error al guardar el pedido:', error);
        alert('Hubo un error al procesar el pedido. Intenta de nuevo.');
    }
});
