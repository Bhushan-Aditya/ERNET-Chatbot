# ERNET Domain Registry Chatbot

A chatbot application to help users register domains and solve queries related to the ERNET domain registry (https://www.registry.ernet.in/).

## Features

- Domain registration assistance
- Query resolution
- User-friendly interface
- Real-time chat interaction

## Project Structure

```
.
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Core functionality
│   │   └── models/   # Data models
│   └── main.py       # Application entry point
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.js
│   └── package.json
└── requirements.txt  # Python dependencies
```

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run the development server:
   ```bash
   npm start
   ```

## Environment Variables

Create a `.env` file in the backend directory with the following variables:
```
OPENAI_API_KEY=your_api_key_here
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 