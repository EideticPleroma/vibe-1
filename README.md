# Personal Finance App

A comprehensive personal finance management application with budgeting and investment tracking features.

## Features

- **Budget Management**: Track income and expenses by category
- **Investment Tracking**: Monitor stocks, crypto, and other investments
- **Transaction History**: Complete record of all financial transactions
- **Data Visualization**: Charts for spending trends and investment growth
- **Predictive Analytics**: Placeholder for investment price forecasting models

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: React with TypeScript
- **Charts**: Chart.js
- **ML Framework**: scikit-learn (placeholder)

## Project Structure

```
vibe-1/
├── backend/                 # Flask backend
│   ├── app.py              # Main Flask application
│   ├── models.py           # Database models
│   ├── routes.py           # API routes
│   ├── database.py         # Database setup
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── types/          # TypeScript types
│   ├── package.json        # Node dependencies
│   └── README.md           # Frontend setup
├── venv/                   # Python Virtual Environment
└── README.md               # This file
```

## Quick Start

To set up and run the application locally, follow these steps:

### Backend Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install backend dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Initialize database:**
   ```bash
   python backend/database.py
   ```

4. **Run Flask app:**
   ```bash
   flask --app backend/app.py run
   ```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory and install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Budget Categories
- `GET /api/categories` - List all categories
- `POST /api/categories` - Create new category
- `PUT /api/categories/<id>` - Update category
- `DELETE /api/categories/<id>` - Delete category

### Transactions
- `GET /api/transactions` - List all transactions
- `POST /api/transactions` - Create new transaction
- `PUT /api/transactions/<id>` - Update transaction
- `DELETE /api/transactions/<id>` - Delete transaction

### Investments
- `GET /api/investments` - List all investments
- `POST /api/investments` - Create new investment
- `PUT /api/investments/<id>` - Update investment
- `DELETE /api/investments/<id>` - Delete investment

## Customization Points

The app includes several areas where you can add your own logic:

1. **Investment Price Updates**: Modify `update_investment_prices()` in `models.py`
2. **Predictive Models**: Add your ML models in `predictive_models.py`
3. **Additional Categories**: Extend the category system in `models.py`
4. **Custom Charts**: Modify Chart.js configurations in React components
5. **Authentication**: Add user authentication system
6. **Data Export**: Implement CSV/PDF export functionality

## Database Schema

### Categories Table
- `id` (Primary Key)
- `name` (Category name)
- `type` (income/expense)
- `color` (Display color)

### Transactions Table
- `id` (Primary Key)
- `date` (Transaction date)
- `amount` (Amount)
- `category_id` (Foreign key to categories)
- `description` (Transaction description)
- `type` (income/expense)

### Investments Table
- `id` (Primary Key)
- `asset_name` (Asset name)
- `asset_type` (stock/crypto/other)
- `quantity` (Quantity owned)
- `purchase_price` (Purchase price per unit)
- `current_price` (Current price per unit)
- `purchase_date` (Purchase date)

## Contributing

Feel free to customize and extend this framework according to your needs. The modular structure makes it easy to add new features while maintaining clean separation of concerns.

## License

This project is open source and available under the MIT License.
