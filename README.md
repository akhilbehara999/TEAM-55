# CareerFlow AI - Intelligent Career Companion

CareerFlow AI is an advanced GenAI-powered platform designed to assist job seekers throughout their career journey. By leveraging cutting-edge artificial intelligence technologies, CareerFlow AI provides personalized, real-time support for resume optimization, interview preparation, contract review, and professional document generation.

## 1. Project Overview

CareerFlow AI addresses critical gaps in traditional career support systems by offering an integrated, intelligent solution that adapts to individual user needs. Our platform combines multiple specialized AI agents to deliver comprehensive career assistance, from initial resume crafting to final contract negotiation.

## 2. Core Features

### Resume Intelligence Agent
Analyzes resumes against job descriptions, identifies skill gaps, suggests keyword optimizations, and provides formatting recommendations to maximize Applicant Tracking System (ATS) compatibility and human recruiter appeal.

### Interview Simulation Agent
Generates realistic, role-specific interview questions, conducts interactive mock interviews with voice interaction, and provides detailed performance feedback with improvement suggestions.

### Contract Guardian Agent
Reviews employment contracts, identifies potential risks and unfavorable clauses, explains legal terminology in plain language, suggests negotiation points, and ensures users understand their rights and obligations before signing agreements.

### Auto-Docs Agent
Generates professional career documents including cover letters, portfolio summaries, achievement trackers, and career progression reports with customizable templates and industry-appropriate formatting.

These agents collaborate through shared context repositories, enabling cross-functional insights and maintaining continuity across different career activities.

## 3. Technology Stack

- **Frontend**: React + TypeScript + Tailwind CSS + Framer Motion
- **Backend**: FastAPI + Python
- **AI Framework**: LangChain + Google Gemini API
- **Database**: SQLite (development) / PostgreSQL (production)
- **Deployment**: Docker containers with Kubernetes orchestration

## 4. Specialized AI Agents

### Resume Intelligence Agent
Optimizes resumes for specific job roles by analyzing job descriptions, identifying missing keywords, suggesting formatting improvements, and ensuring ATS compatibility.

### Interview Simulation Agent
Prepares users for interviews by generating realistic questions, conducting mock interviews with voice interaction, and providing comprehensive feedback on performance.

### Contract Guardian Agent
Reviews employment contracts, identifies potential risks and unfavorable clauses, explains legal terminology in plain language, suggests negotiation points, and ensures users understand their rights and obligations before signing agreements.

### Auto-Docs Agent
Generates professional career documents including cover letters, portfolio summaries, achievement trackers, and career progression reports with customizable templates and industry-appropriate formatting.

## 5. Application Workflow

1. **User Enters Platform**: Access CareerFlow AI through web interface with secure authentication
2. **Selects Career Task**: Choose from resume optimization, interview prep, contract review, or document generation
3. **Agent Activation**: Master Orchestrator activates relevant specialized agents based on user selection
4. **AI Analysis**: Agents process user inputs, reference materials, and contextual data to generate insights
5. **Actionable Output**: Receive personalized recommendations, documents, or interactive coaching sessions

## 6. Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google API Key for Gemini
- Docker (for containerized deployment)

### Installation
1. Clone the repository
2. Install backend dependencies: `pip install -r requirements.txt`
3. Install frontend dependencies: `npm install`
4. Set up environment variables in `.env` file
5. Run the development server: `python start_dev.py`

### Environment Variables
Create a `.env` file with the following variables:
```
GOOGLE_API_KEY=your_google_api_key_here
DATABASE_URL=sqlite:///./careerflow.db
SECRET_KEY=your_secret_key_here
```

## 7. API Endpoints

### Resume Analysis
- `POST /api/analyze/resume` - Analyze resume against job description

### Interview Simulation
- `POST /api/simulate/interview` - Generate interview questions
- `POST /api/submit/interview` - Submit interview answers for feedback

### Contract Analysis
- `POST /api/analyze/contract` - Analyze employment contract for risks

### Document Generation
- `POST /api/autodocs/generate` - Generate professional documents

## 8. Contributing

We welcome contributions to CareerFlow AI! Please fork the repository and submit pull requests with your improvements.

## 9. License

This project is licensed under the MIT License - see the LICENSE file for details.

## 10. Contact

For support or inquiries, please contact the development team at support@careerflow.ai