# Product Management System

A modern web application built with **FastAPI** (backend) and **Streamlit** (frontend) to manage products and suppliers efficiently. It includes user authentication, CRUD operations for products and suppliers, and interactive data visualizations.

---

## Features

- **User Registration & Authentication** with JWT tokens
- **Product Management**: Create, Read, Update, Delete products
- **Supplier Management**: Manage suppliers and their details
- **Interactive Frontend** built with Streamlit
- **Data Visualization**: View charts and tables of products and suppliers
- **Caching** for faster response times on frequently accessed data
- **Async Database Operations** using SQLAlchemy with AsyncSession

---

## Tech Stack

| Layer         | Technology          |
| ------------- | ------------------- |
| Backend API   | FastAPI             |
| Authentication| OAuth2 + JWT Tokens |
| Database      | SQLAlchemy (Async)  |
| Frontend UI   | Streamlit           |
| Caching       | fastapi-cache2      |
| HTTP Client   | requests            |
| Data Models   | Pydantic            |

---

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL or your preferred async-compatible DB (adjust `get_db` dependency)
- [Poetry](https://python-poetry.org/) or pip for package management (optional)

### Installation

```bash
git clone https://github.com/yourusername/product-management-system.git
cd product-management-system

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
