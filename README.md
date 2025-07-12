# Arab Expo Food - Virtual Exhibition Platform

A comprehensive virtual exhibition platform for the food and beverage industry, connecting exhibitors and visitors in the Arab region.

## Features

- **Multi-user System**: Admin, Exhibitor, and Visitor roles
- **Virtual Pavilions**: Interactive exhibition spaces
- **Product Showcase**: Display products with detailed information
- **Mobile Responsive**: Optimized for mobile devices
- **Multi-language Support**: Arabic and English
- **Registration System**: Easy registration for exhibitors and visitors
- **Dashboard Management**: Comprehensive admin and exhibitor dashboards

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with responsive design
- **Icons**: Font Awesome
- **Authentication**: Flask-Login

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/arab-expo-food.git
cd arab-expo-food
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
copy .env.example .env
# Edit .env with your configuration
```

5. Initialize database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
python app.py
```

## Usage

- Visit `http://localhost:5000` to access the application
- Register as an exhibitor or visitor
- Explore virtual pavilions and products
- Admin can manage content through the admin dashboard

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.