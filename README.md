# Inventory Management System

The **Inventory Management System** is a Django-based web application designed to manage inventory items, stock levels, and inventory operations within an organization.

This document provides **complete step-by-step instructions** to install, configure, and run the project on **Ubuntu Linux**, starting from system setup to running the application in a browser.

---

## 🛠️ Technology Stack

- Python 3
- Django
- SQLite (default database)
- HTML, CSS, Bootstrap
- Git
- Ubuntu Linux

---

## 🚀 Installation and Setup (Ubuntu)

```bash
# Update system and install required packages
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# Verify installation
python3 --version
pip3 --version
git --version

# Clone the repository
git clone git@github.com:soonebabu/InventoryManagementSystem.git
cd InventoryManagementSystem

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install project dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create environment configuration file
nano .env

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
