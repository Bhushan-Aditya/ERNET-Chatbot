# ERNET Chatbot Frontend

This is the React frontend for the ERNET Domain Registry Chatbot. It provides a modern, responsive UI for users to interact with the ERNET chatbot, search for domains, and access support information.

## Features
- Modern, responsive UI inspired by the official ERNET registry site
- Floating, animated chatbot widget connected to the FastAPI backend
- Centered navigation bar with smooth underline animation and modern font
- Support for ERNET, G20, and Government of India logos
- Accessibility and language bar
- Beautiful search bar and support info card

## Getting Started

### 1. Prerequisites
- Node.js (v16 or later recommended)
- npm or yarn

### 2. Install Dependencies
```
npm install
# or
yarn install
```

### 3. Add Logo Images
Place the following images in the `public/` directory:
- `ernet-logo.png` (ERNET logo)
- `g20-logo.png` (G20 India logo)
- `gov-logo.png` (Government of India logo)

> **Tip:** Use transparent PNGs for best results. File names must match exactly.

### 4. Start the Development Server
```
npm start
# or
yarn start
```
The app will run at [http://localhost:3000](http://localhost:3000).

### 5. Connect to Backend
Ensure your FastAPI backend is running at `http://localhost:8000` (or update the proxy in `package.json` if needed).

## Backend (FastAPI) Setup
To run the backend with auto-reload for development, use:
```
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```
- Make sure you run this command from the project root directory.
- Adjust the path (`backend.app:app`) if your main FastAPI app is in a different location.

## Customization
- **Navigation Bar:** Edit `src/components/Header.jsx` and `src/index.css` for nav links, layout, and animation.
- **Chatbot Widget:** Edit `src/components/ChatbotWidget.jsx` and `src/components/ChatbotWidget.css` for chat UI and behavior.
- **Branding:** Replace logo images in `public/` as needed.

## Deployment
To build for production:
```
npm run build
# or
yarn build
```

## License
MIT 