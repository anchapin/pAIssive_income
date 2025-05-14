# UI Architecture

## API Server (`ui/api_server.py`)

The API server provides a RESTful interface for the frontend to interact with the backend services. 

### Key Components

- `APIHandler`: Base HTTP request handler with CORS support
- Database integration with PostgreSQL
- Error handling with custom exception classes
- Endpoints:
  - `/health`: Health check endpoint
  - `/api/agent`: GET endpoint for retrieving agent information
  - Other RESTful endpoints for agent interactions

### Error Handling

The API server implements a robust error handling mechanism with custom exceptions:
- `DatabaseError`: Base exception for database-related issues
- `DatabaseConfigError`: Specific exception for configuration issues

### Configuration

The API server requires the following environment variables:
- `DATABASE_URL`: PostgreSQL connection string

## React Frontend (`ui/react_frontend/src/App.js`)

The frontend is built using React and integrates with the `@ag-ui-protocol/ag-ui` package for agent interactions.

### Features

- Theme customization support
- Real-time agent data fetching
- Error handling and loading states
- Action handling with backend integration

### Components

- `App`: Main application component
  - Manages agent state
  - Handles data fetching
  - Implements error handling
  - Processes agent actions

### API Integration

The frontend communicates with the backend through two main endpoints:
- `GET /api/agent`: Fetches agent information
- `POST /api/agent/action`: Submits agent actions

### Theme Configuration

The UI supports customizable theming with the following options:
- Primary color
- Secondary color
- Font family
- Border radius
- Dark mode support

## Getting Started

1. Start the API server:
   ```bash
   python -m ui.api_server
   ```

2. Start the React frontend:
   ```bash
   cd ui/react_frontend
   npm install
   npm start
   ```

## Development Guidelines

When making changes to the UI components:
1. Ensure proper error handling is implemented
2. Maintain CORS configuration for local development
3. Document any new endpoints or theme configurations
4. Test both success and error scenarios
