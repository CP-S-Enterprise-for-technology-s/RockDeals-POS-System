import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from models.models import db, User, Product, Customer, Sale, SaleItem, Category, Supplier
from datetime import datetime, timedelta
import json

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rockdeals.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'rockdeals-secret-key-2024'
    
    # Enable CORS for all routes
    CORS(app, origins="*")
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        # Create sample data if database is empty
        if User.query.count() == 0:
            create_sample_data()
    
    # Dashboard API
    @app.route('/api/dashboard/stats', methods=['GET'])
    def get_dashboard_stats():
        try:
            # Calculate total sales
            total_sales = db.session.query(db.func.sum(Sale.total_amount)).scalar() or 0
            
            # Calculate total orders
            total_orders = Sale.query.count()
            
            # Calculate visitors (simulated data)
            total_visitors = 14987
            
            # Calculate total sold products
            total_sold_products = db.session.query(db.func.sum(SaleItem.quantity)).scalar() or 0
            
            # Calculate percentage changes (simulated)
            sales_change = "+2.08%"
            orders_change = "+12.4%"
            visitors_change = "-2.8%"
            products_change = "+12.1%"
            
            return jsonify({
                'total_sales': f"${total_sales:,.2f}",
                'total_orders': f"{total_orders:,}",
                'total_visitors': f"{total_visitors:,}",
                'total_sold_products': f"{total_sold_products:,}",
                'sales_change': sales_change,
                'orders_change': orders_change,
                'visitors_change': visitors_change,
                'products_change': products_change
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/dashboard/customer-habits', methods=['GET'])
    def get_customer_habits():
        try:
            # Simulated customer habits data
            data = [
                {'month': 'Jan', 'seenProduct': 40000, 'sales': 35000},
                {'month': 'Feb', 'seenProduct': 55000, 'sales': 45000},
                {'month': 'Mar', 'seenProduct': 35000, 'sales': 30000},
                {'month': 'Apr', 'seenProduct': 60000, 'sales': 50000},
                {'month': 'May', 'seenProduct': 45000, 'sales': 40000},
                {'month': 'Jun', 'seenProduct': 55000, 'sales': 48000},
                {'month': 'Jul', 'seenProduct': 40000, 'sales': 35000},
            ]
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/dashboard/product-stats', methods=['GET'])
    def get_product_stats():
        try:
            # Get product statistics by category
            categories = Category.query.all()
            stats = []
            
            for category in categories:
                # Calculate sales for this category
                category_sales = db.session.query(db.func.sum(SaleItem.quantity)).join(Product).filter(Product.category_id == category.id).scalar() or 0
                
                stats.append({
                    'name': category.name,
                    'value': category_sales,
                    'change': f"+{(category_sales % 10) / 10:.1f}%"  # Simulated change
                })
            
            return jsonify({
                'total_sales': sum(stat['value'] for stat in stats),
                'categories': stats
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/dashboard/customer-growth', methods=['GET'])
    def get_customer_growth():
        try:
            # Simulated customer growth data
            data = [
                {'country': 'United States', 'new': 287, 'returning': 2417, 'flag': '🇺🇸'},
                {'country': 'Germany', 'new': 156, 'returning': 1823, 'flag': '🇩🇪'},
                {'country': 'Australia', 'new': 98, 'returning': 1245, 'flag': '🇦🇺'},
                {'country': 'France', 'new': 76, 'returning': 987, 'flag': '🇫🇷'},
            ]
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Products API
    @app.route('/api/products', methods=['GET'])
    def get_products():
        try:
            products = Product.query.all()
            return jsonify([{
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'price': float(p.price),
                'stock_quantity': p.stock_quantity,
                'category_id': p.category_id,
                'supplier_id': p.supplier_id,
                'barcode': p.barcode,
                'created_at': p.created_at.isoformat() if p.created_at else None
            } for p in products])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/products', methods=['POST'])
    def create_product():
        try:
            data = request.get_json()
            product = Product(
                name=data['name'],
                description=data.get('description'),
                price=data['price'],
                stock_quantity=data['stock_quantity'],
                category_id=data.get('category_id'),
                supplier_id=data.get('supplier_id'),
                barcode=data.get('barcode')
            )
            db.session.add(product)
            db.session.commit()
            return jsonify({'message': 'Product created successfully', 'id': product.id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/products/<int:product_id>', methods=['PUT'])
    def update_product(product_id):
        try:
            product = Product.query.get_or_404(product_id)
            data = request.get_json()
            
            product.name = data.get('name', product.name)
            product.description = data.get('description', product.description)
            product.price = data.get('price', product.price)
            product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
            product.category_id = data.get('category_id', product.category_id)
            product.supplier_id = data.get('supplier_id', product.supplier_id)
            product.barcode = data.get('barcode', product.barcode)
            
            db.session.commit()
            return jsonify({'message': 'Product updated successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/products/<int:product_id>', methods=['DELETE'])
    def delete_product(product_id):
        try:
            product = Product.query.get_or_404(product_id)
            db.session.delete(product)
            db.session.commit()
            return jsonify({'message': 'Product deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # Customers API
    @app.route('/api/customers', methods=['GET'])
    def get_customers():
        try:
            customers = Customer.query.all()
            return jsonify([{
                'id': c.id,
                'name': c.name,
                'email': c.email,
                'phone': c.phone,
                'address': c.address,
                'created_at': c.created_at.isoformat() if c.created_at else None
            } for c in customers])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/customers', methods=['POST'])
    def create_customer():
        try:
            data = request.get_json()
            customer = Customer(
                name=data['name'],
                email=data.get('email'),
                phone=data.get('phone'),
                address=data.get('address')
            )
            db.session.add(customer)
            db.session.commit()
            return jsonify({'message': 'Customer created successfully', 'id': customer.id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # Sales API
    @app.route('/api/sales', methods=['GET'])
    def get_sales():
        try:
            sales = Sale.query.all()
            return jsonify([{
                'id': s.id,
                'customer_id': s.customer_id,
                'user_id': s.user_id,
                'total_amount': float(s.total_amount),
                'payment_method': s.payment_method,
                'status': s.status,
                'created_at': s.created_at.isoformat() if s.created_at else None
            } for s in sales])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/sales', methods=['POST'])
    def create_sale():
        try:
            data = request.get_json()
            
            # Create sale
            sale = Sale(
                customer_id=data.get('customer_id'),
                user_id=data.get('user_id', 1),  # Default to user 1
                total_amount=data['total_amount'],
                payment_method=data.get('payment_method', 'cash'),
                status=data.get('status', 'completed')
            )
            db.session.add(sale)
            db.session.flush()  # Get the sale ID
            
            # Create sale items
            for item_data in data.get('items', []):
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['quantity'] * item_data['unit_price']
                )
                db.session.add(sale_item)
                
                # Update product stock
                product = Product.query.get(item_data['product_id'])
                if product:
                    product.stock_quantity -= item_data['quantity']
            
            db.session.commit()
            return jsonify({'message': 'Sale created successfully', 'id': sale.id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # Categories API
    @app.route('/api/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()
            return jsonify([{
                'id': c.id,
                'name': c.name,
                'description': c.description
            } for c in categories])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

def create_sample_data():
    """Create sample data for testing"""
    try:
        # Create categories
        categories = [
            Category(name='Electronics', description='Electronic devices and accessories'),
            Category(name='Games', description='Video games and gaming accessories'),
            Category(name='Furniture', description='Home and office furniture'),
        ]
        for category in categories:
            db.session.add(category)
        
        # Create suppliers
        suppliers = [
            Supplier(name='Tech Supplier Inc.', contact_info='tech@supplier.com'),
            Supplier(name='Game World Ltd.', contact_info='games@world.com'),
            Supplier(name='Furniture Plus', contact_info='info@furnitureplus.com'),
        ]
        for supplier in suppliers:
            db.session.add(supplier)
        
        # Create users
        admin_user = User(
            username='admin',
            email='admin@rockdeals.com',
            password_hash='hashed_password',  # In real app, use proper hashing
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        db.session.add(admin_user)
        
        db.session.commit()
        
        # Create products
        products = [
            Product(name='Laptop', description='High-performance laptop', sku='LAP001', price=999.99, stock_quantity=50, category_id=1, supplier_id=1, barcode='123456789'),
            Product(name='Gaming Mouse', description='RGB gaming mouse', sku='MOU001', price=79.99, stock_quantity=100, category_id=1, supplier_id=1, barcode='123456790'),
            Product(name='Video Game', description='Latest action game', sku='GAM001', price=59.99, stock_quantity=200, category_id=2, supplier_id=2, barcode='123456791'),
            Product(name='Office Chair', description='Ergonomic office chair', sku='FUR001', price=299.99, stock_quantity=30, category_id=3, supplier_id=3, barcode='123456792'),
        ]
        for product in products:
            db.session.add(product)
        
        # Create customers
        customers = [
            Customer(first_name='John', last_name='Doe', email='john@example.com', phone='123-456-7890', address='123 Main St'),
            Customer(first_name='Jane', last_name='Smith', email='jane@example.com', phone='098-765-4321', address='456 Oak Ave'),
        ]
        for customer in customers:
            db.session.add(customer)
        
        db.session.commit()
        
        # Create sample sales
        sale1 = Sale(
            sale_number='SALE-001',
            customer_id=1, 
            user_id=1, 
            subtotal=1079.98,
            total_amount=1079.98, 
            payment_method='credit_card'
        )
        db.session.add(sale1)
        db.session.flush()
        
        sale_items = [
            SaleItem(sale_id=sale1.id, product_id=1, quantity=1, unit_price=999.99, total_price=999.99),
            SaleItem(sale_id=sale1.id, product_id=2, quantity=1, unit_price=79.99, total_price=79.99),
        ]
        for item in sale_items:
            db.session.add(item)
        
        db.session.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating sample data: {e}")

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

