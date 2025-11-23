# Stripe Payment Integration - Django E-commerce Project

A Django-based e-commerce application with Stripe PaymentIntent integration, supporting multi-currency payments (USD/EUR), order management, discounts, and tax calculations.

## 🚀 Features

- **Multi-Currency Support**: Buy items in USD or EUR with automatic currency conversion
- **Stripe PaymentIntent Integration**: Secure payment processing using Stripe Elements
- **Order Management**: Create orders with multiple items, discounts, and taxes
- **Discount System**: Support for percentage-based and fixed amount discounts
- **Tax Calculation**: Configurable tax rates applied to orders
- **Service-Oriented Architecture**: Clean separation of concerns with dedicated service layers
- **Docker Support**: Full Docker and Docker Compose setup for easy deployment
- **Admin Panel**: Django admin interface for managing items, orders, discounts, and taxes

## 🛠 Tech Stack

- **Backend**: Django 5.2.8
- **Database**: SQLite
- **Payment Processing**: Stripe PaymentIntent API
- **Frontend**: HTML, CSS, JavaScript (Stripe.js Elements)
- **Containerization**: Docker & Docker Compose
- **Python**: 3.11

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- Stripe account with API keys

## 🔧 Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd proj
   ```

2. **Create `.env` file** in the project root:
   ```env
   SECRET_KEY=your-django-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

   # Stripe Configuration
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

   # Currency Conversion
   USD_TO_EUR_RATE=0.92
   ```

3. **Build and start containers**:
   ```bash
   docker-compose up --build
   ```

4. **Create superuser** (in a new terminal):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the application**:
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

### Option 2: Local Development

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd proj
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file** in the project root (same as Docker option, but without POSTGRES_* variables)

5. **Run migrations**:
   ```bash
   cd proj
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## 🔑 Environment Variables

### Generate Django Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as your `SECRET_KEY` in the `.env` file.

### Required Variables

Create a `.env` file in the project root with the following variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (True/False) | Yes |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | Yes |
| `STRIPE_SECRET_KEY` | Stripe secret key (starts with `sk_`) | Yes |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (starts with `pk_`) | Yes |
| `USD_TO_EUR_RATE` | Currency conversion rate (default: 0.92) | No |

## 📁 Project Structure

```
proj/
├── proj/                    # Main Django project
│   ├── items/              # Items app
│   │   ├── services/       # Item-related services
│   │   │   └── stripe_service.py
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── orders/             # Orders app
│   │   ├── services/       # Order-related services
│   │   │   ├── stripe_service.py
│   │   │   └── order_service.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── utils.py        # Currency conversion utilities
│   ├── proj/               # Project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── templates/          # HTML templates
│       ├── items/
│       └── orders/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
└── README.md
```

## 🌐 API Endpoints

### Items
- `GET /` - List all items
- `GET /<item_id>/` - Item detail page
- `POST /<item_id>/buy/` - Create PaymentIntent for item
- `GET /success/` - Payment success page
- `GET /cancel/` - Payment cancel page

### Orders
- `GET /orders/` - List all orders
- `GET /orders/create/` - Create order form
- `POST /orders/add/` - Create new order
- `GET /orders/<order_id>/` - Order detail page
- `POST /orders/<order_id>/buy/` - Create PaymentIntent for order
- `GET /orders/<order_id>/success/` - Order payment success
- `GET /orders/<order_id>/cancel/` - Order payment cancel

### Admin
- `GET /admin/` - Django admin panel

## 💳 Stripe Setup

1. **Create a Stripe account** at https://stripe.com
2. **Get your API keys** from https://dashboard.stripe.com/apikeys
   - Use test keys for development (start with `sk_test_` and `pk_test_`)
   - Use live keys for production (start with `sk_live_` and `pk_live_`)
3. **Add keys to `.env` file**:
   ```env
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```

## 👤 Admin Panel Setup

1. **Create superuser**:
   ```bash
   # Docker
   docker-compose exec web python manage.py createsuperuser
   
   # Local
   python manage.py createsuperuser
   ```

2. **Access admin panel**: http://localhost:8000/admin

3. **Login** with your superuser credentials

4. **Mock data is automatically created** on deployment:
   - 8 mock items
   - 7 mock discounts
   - 5 mock taxes
   
   You can also manually add more via the admin panel.

## 🧪 Testing the Application

### Test Payment Flow

1. **Add test items** via admin panel
2. **Create an order**:
   - Go to http://localhost:8000/orders/create/
   - Select items and quantities
   - Choose currency (USD or EUR)
   - Optionally add discount and tax
   - Click "Create Order"
3. **Complete payment**:
   - Click "Proceed to Payment"
   - Use Stripe test card: `4242 4242 4242 4242`
   - Any future expiry date
   - Any 3-digit CVC
   - Any ZIP code
4. **Verify payment**:
   - Order status should update to "Paid"
   - Check Stripe Dashboard for payment details

### Test Currency Conversion

1. **Select EUR currency** on items or order pages
2. **Verify prices convert** from USD to EUR
3. **Complete payment** in EUR
4. **Check Stripe Dashboard** - payment should be in EUR

## 🚢 Deployment

### Upload to GitHub

1. **Initialize Git repository** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create a new repository on GitHub**

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git branch -M main
   git push -u origin main
   ```

### Deploy to Production Platforms

#### Option 1: Railway (Recommended)

1. **Go to** https://railway.app
2. **Create new project** → "Deploy from GitHub repo"
3. **Select your repository**
4. **Railway will automatically detect the Dockerfile** and use it for deployment
5. **Configure environment variables** in Railway dashboard:
   ```
   SECRET_KEY=<generate-strong-key>
   DEBUG=False
   STRIPE_SECRET_KEY=sk_live_... (or sk_test_... for testing)
   STRIPE_PUBLISHABLE_KEY=pk_live_... (or pk_test_... for testing)
   USD_TO_EUR_RATE=0.92
   ```
6. **Deploy** - Railway will automatically:
   - Build the Docker image
   - Run database migrations
   - Create superuser (admin/admin123)
   - Create mock items, discounts, and taxes
   - Collect static files
   - Start the server

**Note**: Migrations, superuser creation, and mock data setup happen automatically on deployment via the entrypoint script.

**Admin Panel**: `https://stripe-payment-production-4a40.up.railway.app/admin`

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY` (use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Use Stripe live keys (`sk_live_...` and `pk_live_...`)
- [ ] Run migrations: `python manage.py migrate` (automatic via entrypoint.sh)
- [ ] Create superuser: `python manage.py createsuperuser` (automatic via entrypoint.sh - admin/admin123)
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Set up SSL/HTTPS (most platforms do this automatically)
- [ ] Test payment flow with real Stripe test cards

## 📝 Usage Examples

### Creating an Order

1. Navigate to `/orders/create/`
2. Select currency (USD or EUR)
3. Choose items and quantities
4. Optionally select discount and tax
5. Click "Create Order"
6. Review order details
7. Click "Proceed to Payment"
8. Enter card details
9. Complete payment

### Buying Individual Items

1. Navigate to `/` (items list)
2. Select currency (USD or EUR)
3. Click "View Details" on any item
4. Click "Buy Now"
5. Enter card details
6. Complete payment

## 🔒 Security Notes

- Never commit `.env` file to version control
- Use strong `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use Stripe live keys only in production
- Keep Stripe API keys secure
- Regularly update dependencies

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset database (Docker)
docker-compose down
docker-compose up --build

# Run migrations manually
docker-compose exec web python manage.py migrate
```

### Payment Issues
- Verify Stripe keys are correct
- Check Stripe Dashboard for errors
- Ensure test mode keys for development
- Check browser console for JavaScript errors

### Static Files
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Stripe Documentation](https://stripe.com/docs)
- [Stripe PaymentIntents Guide](https://stripe.com/docs/payments/payment-intents)
- [Docker Documentation](https://docs.docker.com/)

## 📄 License

This project is open source and available under the MIT License.

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

## 🎯 Quick Start Summary

```bash
# 1. Clone repository
git clone <your-repo-url>
cd proj

# 2. Create .env file with your Stripe keys

# 3. Start with Docker
docker-compose up --build

# 4. Create admin user
docker-compose exec web python manage.py createsuperuser

# 5. Access application
# http://localhost:8000
# http://localhost:8000/admin
```
---

## 🌍 Live Deployment

### Access the Application

**Live URL**: https://stripe-payment-production-4a40.up.railway.app

**Admin Panel**: https://stripe-payment-production-4a40.up.railway.app/admin

### Test Credentials

- **Username**: `admin`
- **Password**: `admin123`

### Testing the Live Application

1. **Browse Items**: Navigate to the home page to see available items
2. **Create Order**: 
   - Go to `/orders/create/`
   - Select items and currency (USD/EUR)
   - Add discount/tax if needed
   - Create order
3. **Test Payment**:
   - Use Stripe test card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., `12/25`)
   - CVC: Any 3 digits (e.g., `123`)
   - ZIP: Any 5 digits (e.g., `12345`)
4. **Admin Panel**:
   - Access `/admin/` with provided credentials
   - Manage items, orders, discounts, and taxes
   - View payment status and order details

### Admin Panel Features

- **Items Management**: Create, edit, delete items (8 mock items are pre-loaded)
- **Orders View**: See all orders with payment status
- **Discounts**: Create percentage or fixed amount discounts (7 mock discounts are pre-loaded)
- **Tax Rates**: Configure tax percentages (5 mock taxes are pre-loaded)
- **Order Details**: View complete order information including items, totals, and payment status

### Pre-loaded Mock Data

The application automatically creates the following mock data on deployment:

**Items (8)**:
- Premium Laptop ($1,299.99)
- Wireless Headphones ($199.99)
- Smart Watch ($299.99)
- Gaming Mouse ($79.99)
- Mechanical Keyboard ($149.99)
- 4K Monitor ($449.99)
- USB-C Hub ($49.99)
- Webcam HD ($89.99)

**Discounts (7)**:
- 10% Off, 20% Off, 15% Off (percentage, USD)
- $50 Off, $25 Off (fixed, USD)
- €30 Off (fixed, EUR)
- 5% Off (percentage, EUR)

**Taxes (5)**:
- Standard Tax (8%), Sales Tax (10%), VAT (20%), Low Tax (5%), High Tax (15%)

---
