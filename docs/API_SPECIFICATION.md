# توثيق API - CP'S Enterprise POS
## API Specification v2.0

**الإصدار:** 2.0.0  
**Base URL:** `https://api.cps-enterprise.com/v1`  
**Content-Type:** `application/json`

---

## 1. المصادقة (Authentication)

### 1.1 تسجيل الدخول

```http
POST /auth/login
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "admin",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "admin",
      "email": "admin@cps-enterprise.com",
      "first_name": "Admin",
      "last_name": "User",
      "role": "admin",
      "avatar_url": "https://cdn.cps-enterprise.com/avatars/admin.png"
    }
  }
}
```

### 1.2 تجديد التوكن

```http
POST /auth/refresh
Content-Type: application/json
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600
  }
}
```

---

## 2. المستخدمين (Users)

### 2.1 الحصول على قائمة المستخدمين

```http
GET /users?page=1&per_page=20&search=john&role=cashier
Authorization: Bearer {access_token}
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | integer | رقم الصفحة (default: 1) |
| per_page | integer | عدد العناصر في الصفحة (default: 20, max: 100) |
| search | string | البحث بالاسم أو البريد |
| role | string | تصفية حسب الدور |
| is_active | boolean | تصفية حسب الحالة |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "john.doe",
      "email": "john@cps-enterprise.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "cashier",
      "is_active": true,
      "created_at": "2026-01-15T10:30:00Z",
      "last_login": "2026-02-14T08:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

### 2.2 إنشاء مستخدم جديد

```http
POST /users
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "jane.smith",
  "email": "jane@cps-enterprise.com",
  "password": "SecurePass123!",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "manager",
  "is_active": true
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "username": "jane.smith",
    "email": "jane@cps-enterprise.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "role": "manager",
    "is_active": true,
    "created_at": "2026-02-14T10:30:00Z"
  },
  "message": "User created successfully"
}
```

### 2.3 تحديث مستخدم

```http
PUT /users/{id}
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith-Updated",
  "role": "admin",
  "is_active": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "username": "jane.smith",
    "email": "jane@cps-enterprise.com",
    "first_name": "Jane",
    "last_name": "Smith-Updated",
    "role": "admin",
    "is_active": true,
    "updated_at": "2026-02-14T11:00:00Z"
  },
  "message": "User updated successfully"
}
```

### 2.4 حذف مستخدم

```http
DELETE /users/{id}
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

## 3. المنتجات (Products)

### 3.1 الحصول على قائمة المنتجات

```http
GET /products?page=1&per_page=20&category_id=1&search=laptop&low_stock=true
Authorization: Bearer {access_token}
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | integer | رقم الصفحة |
| per_page | integer | عدد العناصر |
| category_id | integer | تصفية حسب الفئة |
| search | string | البحث بالاسم أو الباركود |
| low_stock | boolean | المنتجات منخفضة المخزون |
| is_active | boolean | تصفية حسب الحالة |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440100",
      "name": "Wireless Mouse",
      "barcode": "1234567890123",
      "description": "High-quality wireless mouse with ergonomic design",
      "price": 29.99,
      "cost": 15.00,
      "stock_quantity": 45,
      "min_stock_level": 10,
      "category": {
        "id": 1,
        "name": "Electronics"
      },
      "image_url": "https://cdn.cps-enterprise.com/products/mouse.png",
      "is_active": true,
      "created_at": "2026-01-10T10:00:00Z",
      "updated_at": "2026-02-01T12:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 500,
    "total_pages": 25
  }
}
```

### 3.2 إنشاء منتج جديد

```http
POST /products
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Mechanical Keyboard",
  "barcode": "9876543210987",
  "description": "RGB mechanical keyboard with Cherry MX switches",
  "price": 149.99,
  "cost": 80.00,
  "stock_quantity": 100,
  "min_stock_level": 20,
  "category_id": 1,
  "image_url": "https://cdn.cps-enterprise.com/products/keyboard.png",
  "is_active": true
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440101",
    "name": "Mechanical Keyboard",
    "barcode": "9876543210987",
    "description": "RGB mechanical keyboard with Cherry MX switches",
    "price": 149.99,
    "cost": 80.00,
    "stock_quantity": 100,
    "min_stock_level": 20,
    "category": {
      "id": 1,
      "name": "Electronics"
    },
    "image_url": "https://cdn.cps-enterprise.com/products/keyboard.png",
    "is_active": true,
    "created_at": "2026-02-14T10:30:00Z"
  },
  "message": "Product created successfully"
}
```

### 3.3 البحث في المنتجات

```http
GET /products/search?q=laptop&limit=10
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440102",
      "name": "Gaming Laptop Pro",
      "barcode": "1112223334445",
      "price": 1299.99,
      "stock_quantity": 15,
      "category": {
        "id": 1,
        "name": "Electronics"
      },
      "image_url": "https://cdn.cps-enterprise.com/products/laptop.png"
    }
  ],
  "meta": {
    "total_results": 5
  }
}
```

---

## 4. المبيعات (Sales)

### 4.1 الحصول على قائمة المبيعات

```http
GET /sales?page=1&per_page=20&start_date=2026-02-01&end_date=2026-02-14&user_id=xxx
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440200",
      "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "john.doe",
        "first_name": "John",
        "last_name": "Doe"
      },
      "total_amount": 179.98,
      "discount_amount": 10.00,
      "tax_amount": 8.50,
      "final_amount": 178.48,
      "status": "completed",
      "customer_name": "Customer Name",
      "customer_phone": "+1234567890",
      "items_count": 2,
      "created_at": "2026-02-14T10:30:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 1500,
    "total_pages": 75
  }
}
```

### 4.2 إنشاء عملية بيع

```http
POST /sales
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "items": [
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440100",
      "quantity": 2,
      "unit_price": 29.99
    },
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440101",
      "quantity": 1,
      "unit_price": 149.99
    }
  ],
  "discount_amount": 10.00,
  "tax_rate": 5.0,
  "customer_name": "Ahmed Mohammed",
  "customer_phone": "+966501234567",
  "notes": "Customer requested gift wrapping",
  "payment": {
    "method": "card",
    "amount": 178.48,
    "transaction_id": "txn_123456789"
  }
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440201",
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440300",
        "product": {
          "id": "550e8400-e29b-41d4-a716-446655440100",
          "name": "Wireless Mouse",
          "barcode": "1234567890123"
        },
        "quantity": 2,
        "unit_price": 29.99,
        "total_price": 59.98
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440301",
        "product": {
          "id": "550e8400-e29b-41d4-a716-446655440101",
          "name": "Mechanical Keyboard",
          "barcode": "9876543210987"
        },
        "quantity": 1,
        "unit_price": 149.99,
        "total_price": 149.99
      }
    ],
    "total_amount": 209.97,
    "discount_amount": 10.00,
    "tax_amount": 10.00,
    "final_amount": 209.97,
    "status": "completed",
    "customer_name": "Ahmed Mohammed",
    "customer_phone": "+966501234567",
    "notes": "Customer requested gift wrapping",
    "payment": {
      "method": "card",
      "amount": 209.97,
      "transaction_id": "txn_123456789",
      "status": "completed"
    },
    "receipt_url": "https://api.cps-enterprise.com/v1/sales/550e8400-e29b-41d4-a716-446655440201/receipt",
    "created_at": "2026-02-14T10:30:00Z"
  },
  "message": "Sale completed successfully"
}
```

### 4.3 الحصول على تفاصيل عملية بيع

```http
GET /sales/{id}
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440201",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "john.doe",
      "first_name": "John",
      "last_name": "Doe"
    },
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440300",
        "product": {
          "id": "550e8400-e29b-41d4-a716-446655440100",
          "name": "Wireless Mouse",
          "barcode": "1234567890123"
        },
        "quantity": 2,
        "unit_price": 29.99,
        "total_price": 59.98
      }
    ],
    "total_amount": 209.97,
    "discount_amount": 10.00,
    "tax_amount": 10.00,
    "final_amount": 209.97,
    "status": "completed",
    "customer_name": "Ahmed Mohammed",
    "customer_phone": "+966501234567",
    "notes": "Customer requested gift wrapping",
    "payment": {
      "method": "card",
      "amount": 209.97,
      "transaction_id": "txn_123456789",
      "status": "completed"
    },
    "created_at": "2026-02-14T10:30:00Z"
  }
}
```

### 4.4 عملية استرداد

```http
POST /sales/{id}/refund
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "items": [
    {
      "item_id": "550e8400-e29b-41d4-a716-446655440300",
      "quantity": 1,
      "reason": "Defective product"
    }
  ],
  "refund_amount": 29.99,
  "notes": "Customer reported mouse not working"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "refund_id": "550e8400-e29b-41d4-a716-446655440400",
    "sale_id": "550e8400-e29b-41d4-a716-446655440201",
    "refund_amount": 29.99,
    "status": "completed",
    "processed_at": "2026-02-14T11:00:00Z"
  },
  "message": "Refund processed successfully"
}
```

---

## 5. نقطة البيع (POS)

### 5.1 الحصول على منتجات POS

```http
GET /pos/products?category_id=1&search=laptop
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440100",
      "name": "Wireless Mouse",
      "barcode": "1234567890123",
      "price": 29.99,
      "stock_quantity": 45,
      "image_url": "https://cdn.cps-enterprise.com/products/mouse.png",
      "category": {
        "id": 1,
        "name": "Electronics"
      }
    }
  ]
}
```

### 5.2 إتمام عملية الشراء

```http
POST /pos/checkout
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "items": [
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440100",
      "quantity": 1
    }
  ],
  "discount_code": "SAVE10",
  "payment_method": "cash",
  "cash_received": 50.00,
  "customer_name": "Walk-in Customer",
  "notes": "Quick sale"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "sale_id": "550e8400-e29b-41d4-a716-446655440201",
    "total_amount": 29.99,
    "discount_amount": 3.00,
    "tax_amount": 1.35,
    "final_amount": 28.34,
    "cash_received": 50.00,
    "change": 21.66,
    "receipt_url": "https://api.cps-enterprise.com/v1/sales/550e8400-e29b-41d4-a716-446655440201/receipt",
    "receipt_number": "RCP-20260214-001",
    "created_at": "2026-02-14T10:30:00Z"
  },
  "message": "Checkout completed successfully"
}
```

---

## 6. التقارير (Reports)

### 6.1 لوحة التحكم

```http
GET /reports/dashboard?period=today
Authorization: Bearer {access_token}
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| period | string | today, yesterday, week, month, year |
| start_date | date | تاريخ البداية |
| end_date | date | تاريخ النهاية |

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "sales": {
      "total_sales": 15000.00,
      "total_orders": 250,
      "average_order_value": 60.00,
      "change_percentage": 15.5
    },
    "products": {
      "total_products": 500,
      "low_stock_count": 15,
      "top_selling": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440100",
          "name": "Wireless Mouse",
          "sold_quantity": 50,
          "revenue": 1499.50
        }
      ]
    },
    "customers": {
      "total_customers": 1200,
      "new_customers": 50,
      "returning_customers": 200
    },
    "inventory": {
      "total_value": 75000.00,
      "low_stock_alerts": 15
    }
  }
}
```

### 6.2 تقرير المبيعات

```http
GET /reports/sales?start_date=2026-02-01&end_date=2026-02-14&group_by=day
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_sales": 45000.00,
      "total_orders": 750,
      "total_items_sold": 1200,
      "average_order_value": 60.00,
      "total_discounts": 1500.00,
      "total_tax": 2250.00
    },
    "daily_breakdown": [
      {
        "date": "2026-02-14",
        "sales": 5000.00,
        "orders": 85,
        "items_sold": 140
      }
    ],
    "payment_methods": {
      "cash": 20000.00,
      "card": 22000.00,
      "other": 3000.00
    },
    "top_products": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440100",
        "name": "Wireless Mouse",
        "quantity": 150,
        "revenue": 4498.50
      }
    ]
  }
}
```

---

## 7. رموز الأخطاء (Error Codes)

### 7.1 رموز الأخطاء العامة

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | خطأ في التحقق من البيانات |
| `UNAUTHORIZED` | 401 | غير مصرح |
| `FORBIDDEN` | 403 | ممنوع الوصول |
| `NOT_FOUND` | 404 | المورد غير موجود |
| `CONFLICT` | 409 | تعارض في البيانات |
| `RATE_LIMIT_EXCEEDED` | 429 | تجاوز الحد المسموح |
| `INTERNAL_ERROR` | 500 | خطأ داخلي في الخادم |
| `SERVICE_UNAVAILABLE` | 503 | الخدمة غير متوفرة |

### 7.2 رموز أخطاء الأعمال

| Code | Description |
|------|-------------|
| `INSUFFICIENT_STOCK` | المخزون غير كافٍ |
| `INVALID_PAYMENT` | عملية دفع غير صالحة |
| `PRODUCT_INACTIVE` | المنتج غير نشط |
| `SALE_ALREADY_REFUNDED` | العملية مستردة مسبقاً |
| `INVALID_DISCOUNT_CODE` | كود خصم غير صالح |
| `PAYMENT_FAILED` | فشل عملية الدفع |

---

## 8. Rate Limiting

### 8.1 حدود الطلبات

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/auth/*` | 5 requests | 1 minute |
| `/api/*` | 100 requests | 1 minute |
| `/pos/*` | 200 requests | 1 minute |
| `/reports/*` | 50 requests | 1 minute |

### 8.2 رأس Rate Limit

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1707912000
```

---

**© 2026 CP'S™ Enterprise Tech Solution L.L.C.**
