#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if it doesn't exist..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser 'admin' created successfully.")
else:
    print("Superuser 'admin' already exists.")
EOF

echo "Creating mock items..."
python manage.py shell << EOF
from items.models import Item

mock_items = [
    {"name": "Premium Laptop", "description": "High-performance laptop with 16GB RAM and 512GB SSD", "price": 1299.99},
    {"name": "Wireless Headphones", "description": "Noise-cancelling wireless headphones with 30-hour battery", "price": 199.99},
    {"name": "Smart Watch", "description": "Fitness tracker with heart rate monitor and GPS", "price": 299.99},
    {"name": "Gaming Mouse", "description": "RGB gaming mouse with 16000 DPI sensor", "price": 79.99},
    {"name": "Mechanical Keyboard", "description": "RGB mechanical keyboard with Cherry MX switches", "price": 149.99},
    {"name": "4K Monitor", "description": "27-inch 4K UHD monitor with HDR support", "price": 449.99},
    {"name": "USB-C Hub", "description": "7-in-1 USB-C hub with HDMI, USB 3.0, and SD card reader", "price": 49.99},
    {"name": "Webcam HD", "description": "1080p HD webcam with auto-focus and built-in microphone", "price": 89.99},
]

created_count = 0
for item_data in mock_items:
    item, created = Item.objects.get_or_create(
        name=item_data["name"],
        defaults={
            "description": item_data["description"],
            "price": item_data["price"]
        }
    )
    if created:
        created_count += 1
        print(f"Created item: {item.name}")

print(f"Mock items setup complete. Created {created_count} new items.")
EOF

echo "Creating mock discounts..."
python manage.py shell << EOF
from orders.models.discount import Discount

mock_discounts = [
    {"name": "10% Off", "discount_type": "percentage", "value": 10.00, "currency": "usd"},
    {"name": "20% Off", "discount_type": "percentage", "value": 20.00, "currency": "usd"},
    {"name": "15% Off", "discount_type": "percentage", "value": 15.00, "currency": "usd"},
    {"name": "$50 Off", "discount_type": "fixed", "value": 50.00, "currency": "usd"},
    {"name": "$25 Off", "discount_type": "fixed", "value": 25.00, "currency": "usd"},
    {"name": "€30 Off", "discount_type": "fixed", "value": 30.00, "currency": "eur"},
    {"name": "5% Off", "discount_type": "percentage", "value": 5.00, "currency": "eur"},
]

created_count = 0
for discount_data in mock_discounts:
    discount, created = Discount.objects.get_or_create(
        name=discount_data["name"],
        defaults={
            "discount_type": discount_data["discount_type"],
            "value": discount_data["value"],
            "currency": discount_data["currency"]
        }
    )
    if created:
        created_count += 1
        print(f"Created discount: {discount.name}")

print(f"Mock discounts setup complete. Created {created_count} new discounts.")
EOF

echo "Creating mock taxes..."
python manage.py shell << EOF
from orders.models.tax import Tax

mock_taxes = [
    {"name": "Standard Tax", "percentage": 8.00},
    {"name": "Sales Tax", "percentage": 10.00},
    {"name": "VAT", "percentage": 20.00},
    {"name": "Low Tax", "percentage": 5.00},
    {"name": "High Tax", "percentage": 15.00},
]

created_count = 0
for tax_data in mock_taxes:
    tax, created = Tax.objects.get_or_create(
        name=tax_data["name"],
        defaults={
            "percentage": tax_data["percentage"]
        }
    )
    if created:
        created_count += 1
        print(f"Created tax: {tax.name}")

print(f"Mock taxes setup complete. Created {created_count} new taxes.")
EOF

echo "Starting Django development server on port 8000..."
exec python manage.py runserver 0.0.0.0:8000

