document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 3000);
    });
});

function addToCart(productId) {
    fetch('/api/products')
        .then(response => response.json())
        .then(products => {
            const product = products.find(p => p.id === productId);
            if (!product) return;
            
            let cart = JSON.parse(localStorage.getItem('cart') || '[]');
            const existingItem = cart.find(item => item.product_id === productId);
            
            if (existingItem) {
                if (existingItem.quantity < product.stock) {
                    existingItem.quantity += 1;
                } else {
                    alert('Not enough stock!');
                    return;
                }
            } else {
                cart.push({
                    product_id: productId,
                    name: product.name,
                    price: product.price,
                    quantity: 1,
                    max_stock: product.stock
                });
            }
            
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCartDisplay();
        });
}

function removeFromCart(productId) {
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    cart = cart.filter(item => item.product_id !== productId);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartDisplay();
}

function updateQuantity(productId, change) {
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const item = cart.find(item => item.product_id === productId);
    
    if (item) {
        const newQuantity = item.quantity + change;
        if (newQuantity > 0 && newQuantity <= item.max_stock) {
            item.quantity = newQuantity;
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCartDisplay();
        } else if (newQuantity <= 0) {
            removeFromCart(productId);
        }
    }
}

function updateCartDisplay() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const cartItemsContainer = document.getElementById('cartItems');
    const cartTotalElement = document.getElementById('cartTotal');
    const cartCountElement = document.getElementById('cartCount');
    
    if (!cartItemsContainer) return;
    
    let total = 0;
    let count = 0;
    
    cartItemsContainer.innerHTML = cart.map(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        count += item.quantity;
        
        return `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div><strong>${item.name}</strong></div>
                    <small class="text-muted">₹${item.price.toFixed(2)} x ${item.quantity}</small>
                </div>
                <div class="cart-item-controls">
                    <button class="btn btn-sm btn-outline-secondary" onclick="updateQuantity(${item.product_id}, -1)">-</button>
                    <span>${item.quantity}</span>
                    <button class="btn btn-sm btn-outline-secondary" onclick="updateQuantity(${item.product_id}, 1)">+</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeFromCart(${item.product_id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
                <div class="ms-2 fw-bold">₹${itemTotal.toFixed(2)}</div>
            </div>
        `;
    }).join('');
    
    if (cartTotalElement) {
        cartTotalElement.textContent = `₹${total.toFixed(2)}`;
    }
    
    if (cartCountElement) {
        cartCountElement.textContent = count;
    }
}

function clearCart() {
    localStorage.removeItem('cart');
    updateCartDisplay();
}

function checkout() {
    const customerId = document.getElementById('customerSelect').value;
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    
    if (!customerId) {
        alert('Please select or create a customer!');
        return;
    }
    
    if (cart.length === 0) {
        alert('Cart is empty!');
        return;
    }
    
    const checkoutBtn = document.getElementById('checkoutBtn');
    if (checkoutBtn) {
        checkoutBtn.disabled = true;
        checkoutBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Processing...';
    }
    
    fetch('/api/create-bill', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            customer_id: parseInt(customerId),
            items: cart
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            alert(`Error: ${data.message}`);
            if (checkoutBtn) {
                checkoutBtn.disabled = false;
                checkoutBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Pay';
            }
        }
    })
    .catch(error => {
        alert(`Error: ${error.message}`);
        if (checkoutBtn) {
            checkoutBtn.disabled = false;
            checkoutBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Pay';
        }
    });
}

function searchProducts() {
    const searchTerm = document.getElementById('productSearch').value.toLowerCase();
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        const productName = card.querySelector('.card-title').textContent.toLowerCase();
        card.style.display = productName.includes(searchTerm) ? 'block' : 'none';
    });
}

function filterByCategory() {
    const category = document.getElementById('categoryFilter').value;
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        const productCategory = card.dataset.category;
        card.style.display = (category === 'all' || productCategory === category) ? 'block' : 'none';
    });
}
