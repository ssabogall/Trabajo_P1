        const orderList = document.getElementById('order-list');
        const orderTotal = document.getElementById('order-total');
        const checkoutBtn = document.getElementById('checkout-btn');

        let total = 0;
        let orders = [];

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

                orders.push({id, name, price });
                total += price;

                // Create order list item
                const li = document.createElement('li');
                li.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');

                const itemName = document.createElement('span');
                itemName.textContent = name;

                const priceSpan = document.createElement('span');
                priceSpan.textContent = `$${price.toFixed(2)}`;
                priceSpan.classList.add('ms-2');

                // Delete button
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

                // Right side container
                const rightSide = document.createElement('div');
                rightSide.classList.add('d-flex', 'align-items-center');
                rightSide.appendChild(priceSpan);
                rightSide.appendChild(deleteBtn);

                li.appendChild(itemName);
                li.appendChild(rightSide);

                orderList.appendChild(li);

                updateTotal();
            });

            const paymentToggleBtn = document.getElementById('payment-toggle');
            let isTransfer = false;

            paymentToggleBtn.addEventListener('click', () => {
                isTransfer = !isTransfer;
                paymentToggleBtn.textContent = isTransfer ? 'Transfer' : 'Cash';
                paymentToggleBtn.classList.toggle('btn-primary', isTransfer);
                paymentToggleBtn.classList.toggle('btn-outline-primary', !isTransfer);
            });

            checkoutBtn.addEventListener('click', () => {
                console.log(isTransfer);

                let orderDate = new Date().toLocaleString();

                console.log(orderDate);
                for (const order of orders) {
                    // order.name
                    order.date = orderDate;
                    order.paymentMethod = isTransfer ? "Transfer" : "Cash";
                    const jsonString = JSON.stringify(order, null, 3);
                    // console.log(jsonString);
                }   

                fetch('/save_order/', {  // Replace with your actual URL for the view
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ orders })
                })
                

            });

         });

        // Payment toggle
