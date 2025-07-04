# Medicine Stock Management System

A comprehensive Django-based web application for managing medicine inventory, suppliers, transactions, and generating reports for pharmacies and medical facilities.

## Features

### 🏥 Core Functionality
- **Medicine Management**: Add, edit, delete, and track medicines with detailed information
- **Inventory Control**: Real-time stock tracking with low stock alerts
- **Supplier Management**: Maintain supplier information and relationships
- **Transaction Tracking**: Record sales, purchases, and stock adjustments
- **Category Management**: Organize medicines by categories
- **User Authentication**: Secure login system with role-based access

### 📊 Reporting & Analytics
- **Dashboard**: Overview of key metrics and statistics
- **Stock Reports**: Current inventory levels and stock movement
- **Sales Reports**: Sales analytics and trends
- **Supplier Reports**: Supplier performance and order history
- **Financial Reports**: Revenue, expenses, and profit analysis

### 🔧 Additional Features
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Search & Filter**: Advanced search and filtering capabilities
- **Export Data**: Export reports to PDF and Excel formats
- **Audit Trail**: Track all system changes and user activities
- **Multi-user Support**: Different user roles and permissions

## Technology Stack

- **Backend**: Django 4.2+
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: PostgreSQL or MySQL
- **Authentication**: Django's built-in authentication system
- **Styling**: Custom CSS with Bootstrap 5
- **Charts**: Chart.js for data visualization

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- PostgreSQL or MySQL database
- Git (for version control)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd DJANGO
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### For PostgreSQL:
1. Install PostgreSQL and create a database:
```sql
CREATE DATABASE medicine_stock_db;
CREATE USER medicine_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE medicine_stock_db TO medicine_user;
```

#### For MySQL:
1. Install MySQL and create a database:
```sql
CREATE DATABASE medicine_stock_db;
CREATE USER 'medicine_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON medicine_stock_db.* TO 'medicine_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Environment Configuration
1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` file with your database credentials:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_ENGINE=postgresql  # or mysql
DB_NAME=medicine_stock_db
DB_USER=medicine_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432  # or 3306 for MySQL
```

### 6. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

### 8. Collect Static Files
```bash
python manage.py collectstatic
```

### 9. Run the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Usage

### First Time Setup
1. Access the application at `http://127.0.0.1:8000/`
2. Login with your superuser credentials
3. Navigate to the admin panel to set up initial data:
   - Add medicine categories
   - Add suppliers
   - Add medicines
   - Create user accounts for staff

### User Roles
- **Admin**: Full access to all features
- **Manager**: Access to most features except user management
- **Staff**: Limited access to daily operations
- **Viewer**: Read-only access to reports and data

### Key Workflows

#### Adding New Medicine
1. Go to Medicines → Add Medicine
2. Fill in medicine details (name, category, supplier, etc.)
3. Set initial stock quantity
4. Save the medicine

#### Recording a Sale
1. Go to Transactions → New Sale
2. Select medicines and quantities
3. Enter customer information (if required)
4. Complete the transaction

#### Stock Adjustment
1. Go to Transactions → Stock Adjustment
2. Select medicine and adjustment type
3. Enter quantity and reason
4. Submit the adjustment

#### Generating Reports
1. Go to Reports section
2. Select report type and date range
3. Apply filters if needed
4. View or export the report

## Project Structure

```
DJANGO/
├── accounts/                 # User authentication and management
├── dashboard/               # Dashboard views and analytics
├── medicines/               # Medicine and inventory management
├── medicine_stock/          # Main project settings
├── static/                  # Static files (CSS, JS, images)
│   ├── css/
│   └── js/
├── templates/               # HTML templates
│   ├── auth/               # Authentication templates
│   ├── base.html           # Base template
│   ├── categories/         # Category templates
│   ├── dashboard/          # Dashboard templates
│   ├── medicines/          # Medicine templates
│   ├── suppliers/          # Supplier templates
│   └── transactions/       # Transaction templates
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## API Endpoints

The application provides RESTful endpoints for:
- `/api/medicines/` - Medicine CRUD operations
- `/api/suppliers/` - Supplier management
- `/api/transactions/` - Transaction records
- `/api/reports/` - Report generation

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Testing

Run the test suite:
```bash
python manage.py test
```

Run with coverage:
```bash
coverage run --source='.' manage.py test
coverage report
```

## Deployment

### Production Settings
1. Set `DEBUG=False` in your `.env` file
2. Configure a production database
3. Set up a web server (nginx + gunicorn)
4. Configure SSL certificates
5. Set up static file serving
6. Configure email settings for notifications

### Docker Deployment
A `Dockerfile` and `docker-compose.yml` are provided for containerized deployment.

```bash
docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check database credentials in `.env`
   - Ensure database server is running
   - Verify database exists

2. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check `STATIC_URL` and `STATIC_ROOT` settings

3. **Permission Denied Errors**
   - Check file permissions
   - Ensure proper user roles are assigned

4. **Migration Errors**
   - Delete migration files and recreate: `python manage.py makemigrations`
   - Reset database if necessary

### Getting Help
- Check the Django documentation: https://docs.djangoproject.com/
- Review the application logs
- Create an issue in the repository

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django framework and community
- Bootstrap for responsive design
- Chart.js for data visualization
- All contributors and testers

## Changelog

### Version 1.0.0
- Initial release
- Core medicine management features
- User authentication system
- Basic reporting functionality
- Responsive web interface

---

**Note**: This is a development version. For production use, please ensure proper security configurations and testing.#   s t o c k e a s y  
 