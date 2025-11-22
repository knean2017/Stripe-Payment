<<<<<<< HEAD
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
├── docker-entrypoint.sh
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

4. **Add test data**:
   - Create Items (name, description, price)
   - Create Discounts (percentage or fixed amount)
   - Create Tax rates (percentage)

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
4. **Configure environment variables**:
   ```
   SECRET_KEY=<generate-strong-key>
   DEBUG=False
   ALLOWED_HOSTS=*.railway.app,yourdomain.com
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PUBLISHABLE_KEY=pk_live_...
   USD_TO_EUR_RATE=0.92
   ```
5. **Deploy** - Railway will automatically detect Django and deploy
6. **Run migrations**:
   - Go to your service → "Deployments" → "View Logs"
   - Or use Railway CLI: `railway run python manage.py migrate`
7. **Create superuser**:
   - Railway CLI: `railway run python manage.py createsuperuser`
   - Or use Railway's web terminal

**Admin Panel**: `https://your-app.railway.app/admin`

#### Option 2: Render

1. **Go to** https://render.com
2. **Create new "Web Service"**
3. **Connect GitHub repository**
4. **Configure**:
   - **Build Command**: `pip install -r requirements.txt && cd proj && python manage.py collectstatic --noinput`
   - **Start Command**: `cd proj && gunicorn proj.wsgi:application`
5. **Set environment variables**:
   - Use Render's environment variable section
   - Add all required variables from `.env`
6. **Deploy**

**Note**: `gunicorn` is already included in `requirements.txt`

#### Option 3: Vercel (Serverless)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **Set environment variables** in Vercel dashboard

5. **Configure `vercel.json`** (already included in project)

**Note**: Vercel requires special configuration for Django. See `vercel.json` for details.

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY` (use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Use Stripe live keys (`sk_live_...` and `pk_live_...`)
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Set up SSL/HTTPS (most platforms do this automatically)
- [ ] Test payment flow with real Stripe test cards

### Online Deployment Options

- **Vercel**: Serverless Django deployment
- **Railway**: Easy PostgreSQL + Django hosting
- **Render**: Free tier available with PostgreSQL
- **Heroku**: Classic Django hosting platform
- **DigitalOcean App Platform**: Simple container deployment

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

**Live URL**: [Add your deployed URL here after deployment]

**Admin Panel**: [Your deployed URL]/admin

### Test Credentials (if provided)

- **Username**: [admin username]
- **Password**: [admin password]

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

- **Items Management**: Create, edit, delete items
- **Orders View**: See all orders with payment status
- **Discounts**: Create percentage or fixed amount discounts
- **Tax Rates**: Configure tax percentages
- **Order Details**: View complete order information including items, totals, and payment status

---
=======
