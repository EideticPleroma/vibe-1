# Personal Finance App

A comprehensive personal finance management application with budgeting and investment tracking features.

## Features

- **Budget Management**: Track income and expenses by category
- **Investment Tracking**: Monitor stocks, crypto, and other investments
- **Transaction History**: Complete record of all financial transactions
- **Data Visualization**: Charts for spending trends and investment growth
- **Predictive Analytics**: Placeholder for investment price forecasting models

## Current Status

✅ **Fully Functional Features:**
- Dashboard with financial summaries and charts
- Transaction management (create, read, update, delete)
- Category management with budget limits
- Investment tracking and performance analysis
- Spending trends and analytics
- Responsive web interface

✅ **Recent Improvements:**
- One-click startup with `start.bat`
- Comprehensive sample data seeding
- Fixed transaction creation workflow
- Optional transaction descriptions
- Improved error handling and debugging

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

## Prerequisites

To run this application, you will need:

- Python 3.8 or higher installed (download from [python.org](https://www.python.org/downloads/)). When installing, make sure to check the option to add Python to your PATH.
- Node.js 16 or higher installed (download from [nodejs.org](https://nodejs.org/))

## Quick Start

The easiest way to get started is using the provided batch file that handles both backend and frontend setup:

### Option 1: One-Click Startup (Recommended)

1. **Double-click `start.bat`** in the project root directory
2. **Wait for both services to start** - you'll see:
   - Backend starting at `http://localhost:5000`
   - Frontend starting at `http://localhost:3000`
3. **Open your browser** and navigate to `http://localhost:3000`

The batch file automatically:
- Activates the Python virtual environment
- Starts the Flask backend server
- Starts the React development server
- Opens both services in separate terminal windows

**What to Expect:**
1. **First Run**: May take 1-2 minutes to install dependencies and start services
2. **Backend Terminal**: Shows database initialization and API endpoints
3. **Frontend Terminal**: Shows React compilation and development server status
4. **Browser**: Automatically opens to the application dashboard
5. **Sample Data**: The database comes pre-populated with realistic financial data

### Option 2: Manual Setup

If you prefer to start services manually:

#### Backend Setup

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

3. **Seed the database with sample data:**
   ```bash
   cd backend
   python seed_data.py
   ```

4. **Run Flask app:**
   ```bash
   python app.py
   ```

The backend will be available at `http://localhost:5000`

#### Frontend Setup

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

## Troubleshooting

### Common Issues

1. **Transaction Creation Not Working**
   - Ensure both backend and frontend are running
   - Check browser console for any JavaScript errors
   - Verify the backend API is accessible at `http://localhost:5000/health`

2. **No Data Showing in Frontend**
   - Run `python backend/seed_data.py` to populate the database with sample data
   - Check that the backend is running and accessible
   - Verify CORS is properly configured (should work automatically)

3. **Port Already in Use**
   - Backend: Change port in `backend/app.py` (line 95)
   - Frontend: Change port in `frontend/package.json` proxy setting

4. **Database Issues**
   - Delete `backend/instance/finance_app.db` and run `seed_data.py` again
   - Check that all Python dependencies are installed

### Recent Fixes Applied

- ✅ **Transaction Creation**: Fixed form validation and submission logic
- ✅ **Description Field**: Made description optional as requested
- ✅ **Category Selection**: Fixed initial category selection in transaction modal
- ✅ **API Integration**: Resolved CORS and proxy configuration issues
- ✅ **Database Seeding**: Added comprehensive sample data generation

## Development Workflow

### Making Changes

1. **Backend Changes**: Edit Python files in the `backend/` directory
   - Flask will automatically reload on file changes
   - Check the backend terminal for any errors

2. **Frontend Changes**: Edit React/TypeScript files in the `frontend/src/` directory
   - React will automatically reload on file changes
   - Check the frontend terminal for compilation errors

3. **Database Changes**: Modify models in `backend/models.py`
   - Run `python backend/seed_data.py` to reset and reseed the database
   - Or manually update the existing database schema

### Testing Features

- **Dashboard**: Navigate to `/` to see financial overview
- **Transactions**: Go to `/transactions` to manage income/expenses
- **Categories**: Manage budget categories and limits
- **Investments**: Track investment performance
- **Analytics**: View spending trends and patterns

## Contributing

Feel free to customize and extend this framework according to your needs. The modular structure makes it easy to add new features while maintaining clean separation of concerns.

## License

This project is open source and available under the MIT License.
