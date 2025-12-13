# CareerFlow AI Architecture

This document describes the architectural design of CareerFlow AI.

## High-Level Architecture

```mermaid
graph TD
    A[User] --> B[Frontend App]
    B --> C[Backend API]
    C --> D[Master Orchestrator Agent]
    D --> E[Resume Intelligence Agent]
    D --> F[Interview Simulation Agent]
    D --> G[Contract Guardian Agent]
    D --> H[Auto-Docs Agent]
    D --> I[RAG System]
    C --> J[(Database)]
    C --> K[Authentication Service]
```

## Component Descriptions

### Frontend Application
- **Technology**: React + TypeScript + Tailwind CSS + Framer Motion
- **Purpose**: Provides user interface for all career services
- **Features**:
  - Animated landing page
  - Interactive dashboards
  - Real-time feedback displays
  - Responsive design

### Backend API
- **Technology**: FastAPI + Python
- **Purpose**: Serves as the central hub for all application logic
- **Features**:
  - RESTful API endpoints
  - Authentication and authorization
  - Request routing and validation
  - Database integration

### Master Orchestrator Agent
- **Purpose**: Central coordinator for all specialized agents
- **Responsibilities**:
  - Route requests to appropriate agents
  - Manage context sharing between agents
  - Coordinate complex workflows
  - Aggregate responses from multiple agents

### Specialized Agents

#### Resume Intelligence Agent
- **Function**: Resume analysis and optimization
- **Capabilities**:
  - ATS compatibility checking
  - Keyword optimization
  - Formatting suggestions
  - Industry-specific recommendations

#### Interview Simulation Agent
- **Function**: Mock interview generation and feedback
- **Capabilities**:
  - Role-specific question generation
  - Behavioral interview preparation
  - Technical assessment creation
  - Performance feedback

#### Contract Guardian Agent
- **Function**: Employment contract review
- **Capabilities**:
  - Risk identification
  - Clause explanation
  - Negotiation suggestions
  - Legal compliance checking

#### Auto-Docs Agent
- **Function**: Automated document generation
- **Capabilities**:
  - Cover letter creation
  - Portfolio development
  - Achievement documentation
  - Reference letter generation

### Supporting Services

#### RAG System
- **Purpose**: Retrieval-Augmented Generation for enhanced accuracy
- **Components**:
  - Vector database for knowledge storage
  - Embedding models for semantic search
  - Document retrieval mechanisms

#### Database
- **Technology**: SQLite (development) / PostgreSQL (production)
- **Purpose**: Persistent storage for user data and documents
- **Schema**:
  - Users table
  - Documents table
  - Sessions table
  - Feedback records

#### Authentication Service
- **Purpose**: Secure user authentication and session management
- **Features**:
  - JWT-based token system
  - Password hashing and verification
  - Session timeout handling