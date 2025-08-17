# Personal Finance App - Frontend

React frontend for the Personal Finance App with TypeScript, Tailwind CSS, and Chart.js.

## Features

- **Dashboard**: Financial overview with charts and recent transactions
- **Transactions**: CRUD operations for income and expenses
- **Categories**: Budget category management
- **Investments**: Portfolio tracking and performance analysis
- **Analytics**: Spending trends and investment performance charts
- **Responsive Design**: Mobile-first approach with Tailwind CSS

## Tech Stack

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Chart.js** with react-chartjs-2 for data visualization
- **React Router** for navigation
- **Axios** for API communication
- **Lucide React** for icons

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend Flask server running on port 5000

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The build artifacts will be stored in the `build/` directory.

## Project Structure

```
src/
├── components/          # Reusable React components
│   ├── Navigation.tsx  # Main navigation sidebar
│   └── TransactionModal.tsx # Transaction form modal
├── pages/              # Page components
│   ├── Dashboard.tsx   # Main dashboard
│   ├── Transactions.tsx # Transaction management
│   ├── Categories.tsx  # Category management
│   ├── Investments.tsx # Investment tracking
│   └── Analytics.tsx   # Data visualization
├── services/           # API services and utilities
│   └── api.ts         # HTTP client and API functions
├── types/              # TypeScript type definitions
│   └── index.ts       # All app types and interfaces
├── App.tsx             # Main app component
└── index.tsx           # App entry point
```

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## API Integration

The frontend communicates with the Flask backend through the `/api` proxy. All API calls are handled in `src/services/api.ts`.

### Key API Functions

- `categoriesApi` - Category CRUD operations
- `transactionsApi` - Transaction management
- `investmentsApi` - Investment tracking
- `dashboardApi` - Dashboard data
- `analyticsApi` - Analytics and trends

## Styling

The app uses Tailwind CSS for styling with custom component classes defined in `src/index.css`.

### Custom CSS Classes

- `.btn` - Base button styles
- `.btn-primary` - Primary button variant
- `.btn-secondary` - Secondary button variant
- `.btn-success` - Success button variant
- `.btn-danger` - Danger button variant
- `.card` - Card container styles
- `.input` - Form input styles
- `.label` - Form label styles

## Data Visualization

Charts are implemented using Chart.js with the following chart types:

- **Line Charts**: Spending trends over time
- **Bar Charts**: Investment performance comparison
- **Doughnut Charts**: Expense breakdown and portfolio distribution

## Responsive Design

The app is fully responsive with:

- Mobile-first design approach
- Collapsible sidebar navigation
- Responsive grid layouts
- Touch-friendly interactions

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

### Adding New Features

1. Create new components in `src/components/`
2. Add new pages in `src/pages/`
3. Update types in `src/types/index.ts`
4. Add API functions in `src/services/api.ts`
5. Update navigation in `src/components/Navigation.tsx`

### Code Style

- Use TypeScript for all components
- Follow React functional component patterns
- Use Tailwind CSS utility classes
- Implement proper error handling
- Add loading states for async operations

## Troubleshooting

### Common Issues

1. **Backend Connection Error**: Ensure Flask server is running on port 5000
2. **Build Errors**: Clear `node_modules` and reinstall dependencies
3. **Chart Rendering Issues**: Check Chart.js registration in `App.tsx`

### Performance Tips

- Use React.memo for expensive components
- Implement proper loading states
- Optimize chart data processing
- Use pagination for large datasets

## Contributing

1. Follow the existing code structure
2. Add proper TypeScript types
3. Implement responsive design
4. Test on multiple devices
5. Add error handling and loading states

## License

This project is open source and available under the MIT License.
