# Church Procurement System

A comprehensive web-based procurement and asset management system designed specifically for churches, built with Django 4.2.

## 🌟 Features

### Procurement Management
- **Purchase Request Management**
  - Create and track purchase requests
  - Multi-level approval workflow
  - Automated status updates
  - Document attachment support

- **Quotation Management**
  - Multiple quotation tracking per request
  - Quotation comparison tools
  - Supplier performance tracking
  - Best value analysis

- **Purchase Orders**
  - Automated PO generation
  - Order tracking
  - Delivery status monitoring
  - Invoice management

### Asset Management
- **Asset Tracking**
  - Comprehensive asset registration
  - Asset categorization
  - Location tracking
  - Asset lifecycle management

- **Asset Operations**
  - Check-in/check-out system
  - Maintenance scheduling
  - Maintenance history tracking
  - Asset availability status

### Reporting and Analytics
- **Dashboard**
  - Real-time procurement status
  - Asset utilization metrics
  - Supplier performance analytics
  - Budget tracking

- **Export Capabilities**
  - Purchase request reports (CSV)
  - Supplier performance reports (PDF)
  - Asset status reports
  - Maintenance schedules

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

1. Clone the repository
```bash
git clone https://github.com/dickson12/Church_procurement_System.git
cd Church_procurement_System
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run database migrations
```bash
python manage.py migrate
```

5. Create a superuser
```bash
python manage.py createsuperuser
```

6. Run the development server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

### Initial Setup

1. Log in as superuser
2. Set up user groups and permissions
3. Configure initial asset categories
4. Add suppliers and departments

## 💡 Usage

### Procurement Process
1. Users create purchase requests
2. Approvers review and approve/reject requests
3. Procurement team collects quotations
4. System helps compare quotations
5. Purchase orders are generated and tracked
6. Goods receipt and supplier rating

### Asset Management
1. Register new assets
2. Track asset movements
3. Schedule and record maintenance
4. Monitor asset utilization
5. Generate asset reports

## 🛠️ Technology Stack

- **Backend Framework**: Django 4.2
- **Database**: SQLite (default), supports PostgreSQL
- **Frontend**: Bootstrap 5
- **Forms**: django-crispy-forms
- **PDF Generation**: ReportLab
- **Excel Handling**: openpyxl, xlsxwriter
- **Testing**: pytest, coverage

## 🔒 Security Features

- User authentication and authorization
- Role-based access control
- CSRF protection
- Secure password handling
- Input validation and sanitization

## 📊 Data Export Formats

- CSV for tabular data
- PDF for formatted reports
- Excel for detailed analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Dickson Godwin

## 🙏 Acknowledgments

- Django community
- Bootstrap team
- All contributors and testers

## 📞 Support

For support, email dicksongodwin.dg@gmail.com or create an issue in the GitHub repository.

---

Made with ❤️ for churches and religious organizations
