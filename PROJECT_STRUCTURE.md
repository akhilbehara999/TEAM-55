# CareerFlow AI Project Structure

```
TEAM-55/
├── agents/                 # AI agent implementations
│   ├── config.py           # Agent configuration
│   ├── orchestrator.py     # Master orchestrator agent
│   ├── resume_agent.py     # Resume intelligence agent
│   ├── interview_agent.py  # Interview simulation agent
│   ├── contract_agent.py   # Contract guardian agent
│   └── docs_agent.py       # Auto-docs agent
├── api/                    # API routes and endpoints
│   └── routes.py           # API route definitions
├── database/               # Database configuration
│   └── config.py           # Database setup and connection
├── models/                 # Database models
│   └── user.py             # User model definition
├── schemas/                # Pydantic schemas for validation
│   ├── user.py             # User schema definitions
│   └── document.py         # Document schema definitions
├── src/                    # Frontend source code
│   ├── assets/             # Static assets (images, icons, etc.)
│   ├── components/         # React components
│   │   └── LandingPage.tsx # Main landing page component
│   ├── styles/             # CSS and styling files
│   │   └── index.css       # Main CSS file
│   ├── App.tsx             # Main App component
│   ├── main.tsx            # Entry point
│   └── README.md           # Frontend documentation
├── utils/                  # Utility functions
│   └── helpers.py          # Helper functions
├── .env.example            # Example environment variables
├── config.py               # Main application configuration
├── index.html              # HTML template
├── init_db.py              # Database initialization script
├── main.py                 # Main FastAPI application
├── package.json            # Frontend dependencies
├── postcss.config.js       # PostCSS configuration
├── PROJECT_STRUCTURE.md    # This file
├── README.md               # Main project documentation
├── requirements.txt        # Backend dependencies
├── start_dev.py            # Development server starter script
├── tailwind.config.js      # Tailwind CSS configuration
├── test_backend.py         # Backend testing script
├── tsconfig.json           # TypeScript configuration
└── vite.config.ts          # Vite configuration
```

## Component Details

### Frontend (src/)
- Built with React, TypeScript, and Tailwind CSS
- Uses Framer Motion for animations
- Single-page application with animated landing page
- Responsive design for all device sizes

### Backend (Root directory)
- Built with FastAPI for high-performance API
- Implements agent-based architecture
- RESTful API endpoints
- Database integration with SQLAlchemy
- Environment-based configuration

### Agents
Each agent specializes in a specific career domain:
1. **Resume Intelligence Agent**: Analyzes and optimizes resumes
2. **Interview Simulation Agent**: Conducts mock interviews
3. **Contract Guardian Agent**: Reviews employment contracts
4. **Auto-Docs Agent**: Generates career documents
5. **Master Orchestrator Agent**: Coordinates all other agents

## Development Setup

1. **Install Dependencies**:
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   npm install
   ```

2. **Environment Configuration**:
   Copy `.env.example` to `.env` and fill in your values

3. **Database Initialization**:
   ```bash
   python init_db.py
   ```

4. **Run Development Servers**:
   ```bash
   # Option 1: Run separately
   python main.py  # Backend on port 8000
   npm run dev     # Frontend on port 5173
   
   # Option 2: Run both with helper script
   python start_dev.py
   ```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Deployment

The application can be deployed separately:
- Frontend: Any static hosting service (Vercel, Netlify, etc.)
- Backend: Any cloud provider (AWS, GCP, Azure) or containerized deployment