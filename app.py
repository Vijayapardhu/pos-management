import sqlite3
import os
import json
import qrcode
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import io
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pos-management-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pos_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

QR_FOLDER = os.path.join('static', 'qr')
if not os.path.exists(QR_FOLDER):
    os.makedirs(QR_FOLDER)

# ============================================
# DATABASE MODELS
# ============================================

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    products = db.relationship('Product', backref='supplier', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    bill_items = db.relationship('BillItem', backref='product', lazy=True)

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    bills = db.relationship('Bill', backref='customer', lazy=True)

class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    bill_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, default=0)
    payment_status = db.Column(db.String(20), default='pending')
    items = db.relationship('BillItem', backref='bill', lazy=True, cascade='all, delete-orphan')

class BillItem(db.Model):
    __tablename__ = 'bill_items'
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class UPISettings(db.Model):
    __tablename__ = 'upi_settings'
    id = db.Column(db.Integer, primary_key=True)
    upi_id = db.Column(db.String(100), nullable=False)
    shop_name = db.Column(db.String(100), default='My Shop')
    shop_address = db.Column(db.String(200), default='')
    shop_phone = db.Column(db.String(15), default='')
    gst_number = db.Column(db.String(20), default='')
    receipt_footer = db.Column(db.String(200), default='Thank you for shopping! *** Visit Again ***')
    currency_symbol = db.Column(db.String(5), default='₹')
    tax_rate = db.Column(db.Float, default=0.0)

# ============================================
# DATABASE INITIALIZATION
# ============================================

def init_db():
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if Category.query.first() is not None:
            return
        
        # Seed sample data
        categories = [
            Category(id=1, name='Grocery'),
            Category(id=2, name='Beverages'),
            Category(id=3, name='Snacks'),
            Category(id=4, name='Dairy'),
            Category(id=5, name='Personal Care')
        ]
        
        suppliers = [
            Supplier(id=1, name='Bharat Wholesale', phone='9822012345'),
            Supplier(id=2, name='Fresh Foods Co.', phone='9923045678')
        ]
        
        products = [
            Product(id=101, name='Basmati Rice 5kg', category_id=1, supplier_id=1, price=550.00, stock=40),
            Product(id=102, name='Coca Cola 750ml', category_id=2, supplier_id=1, price=45.00, stock=120),
            Product(id=103, name='Potato Chips', category_id=3, supplier_id=2, price=20.00, stock=200),
            Product(id=104, name='Amul Milk 500ml', category_id=4, supplier_id=2, price=26.00, stock=80),
            Product(id=105, name='Toothpaste 100g', category_id=5, supplier_id=1, price=65.00, stock=60)
        ]
        
        customers = [
            Customer(id=1, name='Rahul Sharma', phone='9812345678'),
            Customer(id=2, name='Priya Patel', phone='9823456789'),
            Customer(id=3, name='Amit Verma', phone='9834567890')
        ]
        
        for c in categories:
            db.session.add(c)
        for s in suppliers:
            db.session.add(s)
        for p in products:
            db.session.add(p)
        for c in customers:
            db.session.add(c)
        
        db.session.commit()
        
        # Add default UPI settings
        if not get_upi_settings():
            upi_settings = UPISettings(
                upi_id='shop@upi',
                shop_name='My Shop',
                shop_address='',
                shop_phone='',
                gst_number='',
                receipt_footer='Thank you for shopping! *** Visit Again ***',
                currency_symbol='₹',
                tax_rate=0.0
            )
            db.session.add(upi_settings)
            db.session.commit()
        
        print("Database initialized with sample data!")

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_bill_total(bill_id):
    bill = Bill.query.get(bill_id)
    if bill:
        bill.total_amount = sum(item.price * item.quantity for item in bill.items)
        db.session.commit()
    return bill.total_amount if bill else 0

# ============================================
# UPI HELPERS
# ============================================

def get_upi_settings():
    return UPISettings.query.first()

def generate_upi_qr(upi_id, amount, shop_name='Shop'):
    qr_data = f"upi://pay?pa={upi_id}&pn={shop_name}&am={amount:.2f}&cu=INR"
    qr = qrcode.make(qr_data)
    safe_upi = upi_id.split('@')[0].replace(' ', '_')
    filename = f'qr_{safe_upi}_{amount:.0f}.png'
    qr_path = os.path.join(QR_FOLDER, filename)
    qr.save(qr_path)
    return f'qr/{filename}'

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    total_products = Product.query.count()
    total_customers = Customer.query.count()
    total_bills = Bill.query.count()
    low_stock_count = Product.query.filter(Product.stock < 50).count()
    
    # Recent bills
    recent_bills = Bill.query.order_by(Bill.bill_date.desc()).limit(5).all()
    
    # Best selling products
    best_sellers = db.session.query(
        Product.name,
        func.sum(BillItem.quantity).label('total_sold')
    ).join(BillItem).group_by(Product.id).order_by(func.sum(BillItem.quantity).desc()).limit(5).all()
    
    return render_template('index.html', 
                         total_products=total_products,
                         total_customers=total_customers,
                         total_bills=total_bills,
                         low_stock_count=low_stock_count,
                         recent_bills=recent_bills,
                         best_sellers=best_sellers)

# ---- INVENTORY ROUTES ----

@app.route('/inventory')
def inventory():
    products = Product.query.all()
    categories = Category.query.all()
    suppliers = Supplier.query.all()
    return render_template('inventory.html', products=products, categories=categories, suppliers=suppliers)

@app.route('/inventory/add', methods=['POST'])
def add_product():
    try:
        product = Product(
            name=request.form['name'],
            category_id=request.form['category_id'],
            supplier_id=request.form['supplier_id'],
            price=float(request.form['price']),
            stock=int(request.form['stock'])
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding product: {str(e)}', 'error')
    return redirect(url_for('inventory'))

@app.route('/inventory/update/<int:id>', methods=['POST'])
def update_product(id):
    try:
        product = Product.query.get_or_404(id)
        product.name = request.form['name']
        product.category_id = request.form['category_id']
        product.supplier_id = request.form['supplier_id']
        product.price = float(request.form['price'])
        product.stock = int(request.form['stock'])
        db.session.commit()
        flash('Product updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating product: {str(e)}', 'error')
    return redirect(url_for('inventory'))

@app.route('/inventory/delete/<int:id>')
def delete_product(id):
    try:
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'error')
    return redirect(url_for('inventory'))

# ---- POS / BILLING ROUTES ----

@app.route('/pos')
def pos():
    products = Product.query.filter(Product.stock > 0).all()
    customers = Customer.query.all()
    return render_template('pos.html', products=products, customers=customers)

@app.route('/pos/bill')
def pos_bill():
    customers = Customer.query.all()
    return render_template('pos_bill.html', customers=customers)

@app.route('/api/products')
def api_products():
    products = Product.query.filter(Product.stock > 0).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'stock': p.stock,
        'category': p.category.name if p.category else ''
    } for p in products])

@app.route('/api/customers')
def api_customers():
    customers = Customer.query.all()
    return jsonify([{'id': c.id, 'name': c.name, 'phone': c.phone} for c in customers])

@app.route('/api/create-bill', methods=['POST'])
def create_bill():
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        items = data.get('items', [])
        
        if not items:
            return jsonify({'success': False, 'message': 'No items in bill'})
        
        bill = Bill(customer_id=customer_id)
        db.session.add(bill)
        db.session.flush()
        
        for item in items:
            product = Product.query.get(item['product_id'])
            if product and product.stock >= item['quantity']:
                bill_item = BillItem(
                    bill_id=bill.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    price=product.price
                )
                db.session.add(bill_item)
                product.stock -= item['quantity']
            else:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'Insufficient stock for {product.name}'})
        
        db.session.commit()
        get_bill_total(bill.id)
        
        return jsonify({'success': True, 'bill_id': bill.id, 'redirect': url_for('upi_payment', bill_id=bill.id)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# ---- BILLS / RECEIPT ROUTES ----

@app.route('/bills')
def bills():
    bills_list = Bill.query.order_by(Bill.bill_date.desc()).all()
    return render_template('bills.html', bills=bills_list)

@app.route('/bill/<int:bill_id>')
def bill_detail(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    settings = get_upi_settings()
    return render_template('receipt.html', bill=bill, settings=settings)

@app.route('/bill/<int:bill_id>/print')
def print_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    settings = get_upi_settings()
    return render_template('receipt_print.html', bill=bill, settings=settings)

# ---- CUSTOMERS ROUTES ----

@app.route('/customers')
def customers():
    customers_list = Customer.query.all()
    return render_template('customers.html', customers=customers_list)

@app.route('/api/customers', methods=['POST'])
def api_create_customer():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Customer name is required'})
        
        customer = Customer(name=name, phone=phone)
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/customers/add', methods=['POST'])
def add_customer():
    try:
        customer = Customer(
            name=request.form['name'],
            phone=request.form.get('phone', '')
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding customer: {str(e)}', 'error')
    return redirect(url_for('customers'))

# ---- REPORTS ROUTES ----

@app.route('/reports')
def reports():
    # Daily sales
    daily_sales = db.session.query(
        func.date(Bill.bill_date).label('date'),
        func.sum(Bill.total_amount).label('total')
    ).group_by(func.date(Bill.bill_date)).order_by(func.date(Bill.bill_date).desc()).all()
    
    # Best sellers
    best_sellers = db.session.query(
        Product.name,
        func.sum(BillItem.quantity).label('total_sold')
    ).join(BillItem).group_by(Product.id).order_by(func.sum(BillItem.quantity).desc()).all()
    
    # Low stock
    low_stock = Product.query.filter(Product.stock < 50).all()
    
    # Category-wise sales
    category_sales = db.session.query(
        Category.name,
        func.sum(BillItem.quantity * BillItem.price).label('total')
    ).join(Product, BillItem.product_id == Product.id).join(Category).group_by(Category.id).all()
    
    return render_template('reports.html',
                         daily_sales=daily_sales,
                         best_sellers=best_sellers,
                         low_stock=low_stock,
                         category_sales=category_sales)

# ---- CATEGORIES & SUPPLIERS ROUTES ----

@app.route('/categories')
def categories():
    cats = Category.query.all()
    return render_template('categories.html', categories=cats)

@app.route('/categories/add', methods=['POST'])
def add_category():
    try:
        category = Category(name=request.form['name'])
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding category: {str(e)}', 'error')
    return redirect(url_for('categories'))

@app.route('/suppliers')
def suppliers():
    sups = Supplier.query.all()
    return render_template('suppliers.html', suppliers=sups)

@app.route('/suppliers/add', methods=['POST'])
def add_supplier():
    try:
        supplier = Supplier(
            name=request.form['name'],
            phone=request.form.get('phone', '')
        )
        db.session.add(supplier)
        db.session.commit()
        flash('Supplier added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding supplier: {str(e)}', 'error')
    return redirect(url_for('suppliers'))

# ---- UPI / PAYMENT ROUTES ----

@app.route('/upi-settings', methods=['GET', 'POST'])
def upi_settings():
    settings = get_upi_settings()
    if request.method == 'POST':
        upi_id = request.form.get('upi_id', '').strip()
        shop_name = request.form.get('shop_name', 'My Shop').strip()
        shop_address = request.form.get('shop_address', '').strip()
        shop_phone = request.form.get('shop_phone', '').strip()
        gst_number = request.form.get('gst_number', '').strip()
        receipt_footer = request.form.get('receipt_footer', 'Thank you for shopping! *** Visit Again ***').strip()
        currency_symbol = request.form.get('currency_symbol', '₹').strip()
        tax_rate = float(request.form.get('tax_rate', 0))
        
        if not upi_id:
            flash('UPI ID is required', 'error')
            return redirect(url_for('upi_settings'))
        
        if settings:
            settings.upi_id = upi_id
            settings.shop_name = shop_name
            settings.shop_address = shop_address
            settings.shop_phone = shop_phone
            settings.gst_number = gst_number
            settings.receipt_footer = receipt_footer
            settings.currency_symbol = currency_symbol
            settings.tax_rate = tax_rate
        else:
            settings = UPISettings(
                upi_id=upi_id,
                shop_name=shop_name,
                shop_address=shop_address,
                shop_phone=shop_phone,
                gst_number=gst_number,
                receipt_footer=receipt_footer,
                currency_symbol=currency_symbol,
                tax_rate=tax_rate
            )
            db.session.add(settings)
        db.session.commit()
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('upi_settings'))
    return render_template('upi_settings.html', settings=settings)

@app.route('/upi-payment/<int:bill_id>')
def upi_payment(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    settings = get_upi_settings()
    if not settings:
        flash('Please configure UPI settings first', 'error')
        return redirect(url_for('upi_settings'))
    qr_path = generate_upi_qr(settings.upi_id, bill.total_amount, settings.shop_name)
    return render_template('upi_payment.html', bill=bill, settings=settings, qr_path=qr_path)

@app.route('/payment-success/<int:bill_id>')
def payment_success(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    bill.payment_status = 'paid'
    db.session.commit()
    return render_template('payment_success.html', bill=bill)

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('pos_management.db'):
            db.create_all()
            init_db()
            if not get_upi_settings():
                db.session.add(UPISettings(upi_id='shop@upi', shop_name='My Shop'))
                db.session.commit()
        else:
            db.create_all()
            if not get_upi_settings():
                db.session.add(UPISettings(upi_id='shop@upi', shop_name='My Shop'))
                db.session.commit()
    app.run(debug=True)
