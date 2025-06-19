import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Plus, 
  Minus, 
  Trash2, 
  CreditCard, 
  DollarSign,
  Calculator,
  ShoppingCart,
  User,
  Barcode,
  Receipt
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const POS = () => {
  const [cart, setCart] = useState([]);
  const [products, setProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [amountPaid, setAmountPaid] = useState('');
  const [discount, setDiscount] = useState(0);
  const [tax, setTax] = useState(15); // 15% tax

  // Sample products data
  useEffect(() => {
    const sampleProducts = [
      { id: 1, name: 'Laptop', price: 999.99, stock: 50, barcode: '123456789', category: 'Electronics' },
      { id: 2, name: 'Gaming Mouse', price: 79.99, stock: 100, barcode: '123456790', category: 'Electronics' },
      { id: 3, name: 'Video Game', price: 59.99, stock: 200, barcode: '123456791', category: 'Games' },
      { id: 4, name: 'Office Chair', price: 299.99, stock: 30, barcode: '123456792', category: 'Furniture' },
      { id: 5, name: 'Wireless Headphones', price: 149.99, stock: 75, barcode: '123456793', category: 'Electronics' },
      { id: 6, name: 'Desk Lamp', price: 39.99, stock: 120, barcode: '123456794', category: 'Furniture' },
    ];
    setProducts(sampleProducts);
  }, []);

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.barcode.includes(searchTerm)
  );

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
      setCart(cart.map(item =>
        item.id === product.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const updateQuantity = (id, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(id);
    } else {
      setCart(cart.map(item =>
        item.id === id ? { ...item, quantity: newQuantity } : item
      ));
    }
  };

  const removeFromCart = (id) => {
    setCart(cart.filter(item => item.id !== id));
  };

  const clearCart = () => {
    setCart([]);
    setSelectedCustomer(null);
    setAmountPaid('');
    setDiscount(0);
  };

  const calculateSubtotal = () => {
    return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  };

  const calculateDiscountAmount = () => {
    return calculateSubtotal() * (discount / 100);
  };

  const calculateTaxAmount = () => {
    return (calculateSubtotal() - calculateDiscountAmount()) * (tax / 100);
  };

  const calculateTotal = () => {
    return calculateSubtotal() - calculateDiscountAmount() + calculateTaxAmount();
  };

  const calculateChange = () => {
    const paid = parseFloat(amountPaid) || 0;
    const total = calculateTotal();
    return Math.max(0, paid - total);
  };

  const processSale = () => {
    if (cart.length === 0) {
      alert('Cart is empty!');
      return;
    }

    const total = calculateTotal();
    const paid = parseFloat(amountPaid) || 0;

    if (paymentMethod === 'cash' && paid < total) {
      alert('Insufficient payment amount!');
      return;
    }

    // Here you would typically send the sale data to your backend
    const saleData = {
      items: cart,
      customer: selectedCustomer,
      subtotal: calculateSubtotal(),
      discount: calculateDiscountAmount(),
      tax: calculateTaxAmount(),
      total: total,
      paymentMethod: paymentMethod,
      amountPaid: paid,
      change: calculateChange(),
      timestamp: new Date().toISOString()
    };

    console.log('Processing sale:', saleData);
    alert('Sale completed successfully!');
    clearCart();
  };

  const ProductCard = ({ product }) => (
    <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => addToCart(product)}>
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-semibold text-sm">{product.name}</h3>
          <span className="text-lg font-bold text-primary">${product.price}</span>
        </div>
        <div className="flex justify-between items-center text-xs text-muted-foreground">
          <span>{product.category}</span>
          <span>Stock: {product.stock}</span>
        </div>
        <div className="mt-2 text-xs text-muted-foreground">
          Barcode: {product.barcode}
        </div>
      </CardContent>
    </Card>
  );

  const CartItem = ({ item }) => (
    <div className="flex items-center justify-between p-3 border-b">
      <div className="flex-1">
        <h4 className="font-medium">{item.name}</h4>
        <p className="text-sm text-muted-foreground">${item.price} each</p>
      </div>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => updateQuantity(item.id, item.quantity - 1)}
        >
          <Minus className="w-3 h-3" />
        </Button>
        <span className="w-8 text-center">{item.quantity}</span>
        <Button
          variant="outline"
          size="sm"
          onClick={() => updateQuantity(item.id, item.quantity + 1)}
        >
          <Plus className="w-3 h-3" />
        </Button>
        <Button
          variant="destructive"
          size="sm"
          onClick={() => removeFromCart(item.id)}
        >
          <Trash2 className="w-3 h-3" />
        </Button>
      </div>
      <div className="w-20 text-right font-medium">
        ${(item.price * item.quantity).toFixed(2)}
      </div>
    </div>
  );

  return (
    <div className="h-screen flex bg-background">
      {/* Left Panel - Products */}
      <div className="flex-1 p-6 overflow-hidden">
        <div className="h-full flex flex-col">
          {/* Search Bar */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search products by name or barcode..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Products Grid */}
          <div className="flex-1 overflow-y-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredProducts.map(product => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Cart & Checkout */}
      <div className="w-96 bg-card border-l border-border flex flex-col">
        {/* Cart Header */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <ShoppingCart className="w-5 h-5" />
              Cart ({cart.length})
            </h2>
            <Button variant="outline" size="sm" onClick={clearCart}>
              Clear All
            </Button>
          </div>
        </div>

        {/* Customer Selection */}
        <div className="p-4 border-b border-border">
          <Button variant="outline" className="w-full justify-start">
            <User className="w-4 h-4 mr-2" />
            {selectedCustomer ? selectedCustomer.name : 'Select Customer (Optional)'}
          </Button>
        </div>

        {/* Cart Items */}
        <div className="flex-1 overflow-y-auto">
          {cart.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="text-center">
                <ShoppingCart className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Cart is empty</p>
                <p className="text-sm">Add products to get started</p>
              </div>
            </div>
          ) : (
            cart.map(item => <CartItem key={item.id} item={item} />)
          )}
        </div>

        {/* Cart Summary */}
        {cart.length > 0 && (
          <div className="p-4 border-t border-border space-y-4">
            {/* Discount Input */}
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium">Discount %:</label>
              <Input
                type="number"
                value={discount}
                onChange={(e) => setDiscount(Math.max(0, Math.min(100, parseFloat(e.target.value) || 0)))}
                className="w-20"
                min="0"
                max="100"
              />
            </div>

            {/* Summary */}
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Subtotal:</span>
                <span>${calculateSubtotal().toFixed(2)}</span>
              </div>
              {discount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Discount ({discount}%):</span>
                  <span>-${calculateDiscountAmount().toFixed(2)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span>Tax ({tax}%):</span>
                <span>${calculateTaxAmount().toFixed(2)}</span>
              </div>
              <div className="flex justify-between font-bold text-lg border-t pt-2">
                <span>Total:</span>
                <span>${calculateTotal().toFixed(2)}</span>
              </div>
            </div>

            {/* Payment Method */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Payment Method:</label>
              <div className="grid grid-cols-2 gap-2">
                <Button
                  variant={paymentMethod === 'cash' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPaymentMethod('cash')}
                >
                  <DollarSign className="w-4 h-4 mr-1" />
                  Cash
                </Button>
                <Button
                  variant={paymentMethod === 'card' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPaymentMethod('card')}
                >
                  <CreditCard className="w-4 h-4 mr-1" />
                  Card
                </Button>
              </div>
            </div>

            {/* Amount Paid (for cash) */}
            {paymentMethod === 'cash' && (
              <div className="space-y-2">
                <label className="text-sm font-medium">Amount Paid:</label>
                <Input
                  type="number"
                  value={amountPaid}
                  onChange={(e) => setAmountPaid(e.target.value)}
                  placeholder="0.00"
                  step="0.01"
                />
                {amountPaid && (
                  <div className="text-sm">
                    <span>Change: </span>
                    <span className="font-bold">${calculateChange().toFixed(2)}</span>
                  </div>
                )}
              </div>
            )}

            {/* Process Sale Button */}
            <Button 
              className="w-full rockdeals-gradient text-white font-medium"
              onClick={processSale}
              size="lg"
            >
              <Receipt className="w-4 h-4 mr-2" />
              Process Sale
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default POS;

