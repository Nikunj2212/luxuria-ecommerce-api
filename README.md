# Luxuria Ecommerce Backend API

Luxuria is a full-featured **Ecommerce Backend System** built using **Python, Django, and Django REST Framework**.  
The project provides a complete REST API for an ecommerce platform including product management, cart system, wishlist functionality, order management, order tracking, product reviews and ratings, deals and discounts system, and a customer support ticket system.

This backend is designed to simulate a **real-world ecommerce architecture** with secure authentication and scalable API structure.

---

# Tech Stack

### Backend
- Python
- Django
- Django REST Framework
- JWT Authentication

### Frontend
- HTML
- CSS
- JavaScript
- Bootstrap
- Django Templates

### Database
- SQLite

### Tools
- Git
- GitHub
- Postman

---

# Features

## Authentication System
- Secure user authentication
- JWT based login system
- Forgot password functionality
- OTP verification system
- Profile management

---

## Product Management
- Product listing API
- Product detail API
- Category and Subcategory system
- Product search and filtering
- Pagination support

---

## Cart System
- Add product to cart
- Update cart quantity
- Remove product from cart
- Cart summary API
- Total price calculation

---

## Wishlist System
- Add product to wishlist
- Remove from wishlist
- View user's wishlist

---

## Order Management
- Create order
- My orders API
- Order details API
- Order tracking system
- Payment method support

---

## Product Reviews
- Add product review
- View product reviews
- Rating system
- Average rating calculation

---

## Deals and Discounts
- Deal based discount system
- Active deal detection
- Discounted price calculation

---

## Recommendation System
- Trending products
- Top rated products
- Related products
- Recommended products

---

## Customer Support System
- Contact support API
- Ticket based support system
- User and admin messaging
- Ticket status (Open / Closed)

---

# API Endpoints

### Products

| Method | Endpoint | Description |
|------|---------|-------------|
| GET | /api/products/ | Get list of products |
| GET | /api/products/{id}/ | Product details |
| GET | /api/products/{id}/related/ | Related products |
| GET | /api/products/{id}/recommendations/ | Recommended products |
| GET | /api/top-products/ | Top rated products |
| GET | /api/trending-products/ | Trending products |
| GET | /api/deals/ | Active deals |

---

### Cart

| Method | Endpoint | Description |
|------|---------|-------------|
| GET | /api/cart/ | View cart |
| POST | /api/cart/add/ | Add product to cart |
| PUT | /api/cart/update/ | Update cart quantity |
| DELETE | /api/cart/remove/ | Remove product from cart |
| GET | /api/cart/summary/ | Cart summary |

---

### Orders

| Method | Endpoint | Description |
|------|---------|-------------|
| POST | /api/order/create/ | Create order |
| GET | /api/my-orders/ | View user orders |
| GET | /api/order/{id}/ | Order details |
| GET | /api/order/track/{order_id}/ | Track order |

---

### Wishlist

| Method | Endpoint | Description |
|------|---------|-------------|
| POST | /api/wishlist/add/ | Add to wishlist |
| GET | /api/wishlist/ | View wishlist |
| DELETE | /api/wishlist/remove/ | Remove from wishlist |

---

### Reviews

| Method | Endpoint | Description |
|------|---------|-------------|
| POST | /api/product/review/ | Add product review |
| GET | /api/product/{id}/reviews/ | Get product reviews |

---

### Customer Support

| Method | Endpoint | Description |
|------|---------|-------------|
| POST | /api/contact/ | Create support ticket |

---

# Project Structure


luxuria-ecommerce-api/

accounts/ # User authentication and profile management
api/ # REST API endpoints
carts/ # Cart and order management
contact/ # Customer support system
core/ # Main Django project settings
dashboard/ # Admin dashboard features
products/ # Product and category management
wishlist/ # Wishlist functionality
media/ # Uploaded product images
manage.py # Django project entry point


---

# Project Setup

### Clone the repository


git clone https://github.com/Nikunj2212/luxuria-ecommerce-api.git


### Navigate to project


cd luxuria-ecommerce-api


### Create virtual environment


python -m venv venv


### Activate virtual environment

Windows


venv\Scripts\activate


Mac/Linux


source venv/bin/activate


### Install dependencies


pip install -r requirements.txt


### Apply migrations


python manage.py migrate


### Run server


python manage.py runserver


Open browser


http://127.0.0.1:8000/


---

# Author

**Nikunj Panchal**

Backend Developer  
Python | Django | Django REST Framework
