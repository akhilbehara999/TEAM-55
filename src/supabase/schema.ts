// Define the schema for Supabase tables

// Users table (managed by Supabase Auth, but we can extend it)
/*
Table: users (extends Supabase auth.users)
Columns:
- id (UUID) - from auth.users
- full_name (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
*/

// Interview sessions table
/*
Table: interview_sessions
Columns:
- id (UUID) - Primary key
- user_id (UUID) - Foreign key to auth.users
- role (TEXT) - The role being interviewed for
- experience_level (TEXT) - Experience level selected
- started_at (TIMESTAMP) - When the interview started
- completed_at (TIMESTAMP) - When the interview was completed (nullable)
- status (TEXT) - 'in_progress', 'completed', 'cancelled'
- final_score (INTEGER) - Final score if completed
- overall_feedback (TEXT) - Overall feedback if completed
- strengths (JSON) - Array of strengths if completed
- weaknesses (JSON) - Array of weaknesses if completed
*/

// Interview questions table
/*
Table: interview_questions
Columns:
- id (UUID) - Primary key
- session_id (UUID) - Foreign key to interview_sessions
- question_number (INTEGER) - Question sequence number
- question_text (TEXT) - The question asked
- audio_url (TEXT) - URL to the audio file
- created_at (TIMESTAMP) - When the question was created
*/

// User answers table
/*
Table: user_answers
Columns:
- id (UUID) - Primary key
- session_id (UUID) - Foreign key to interview_sessions
- question_id (UUID) - Foreign key to interview_questions
- answer_text (TEXT) - The user's answer
- created_at (TIMESTAMP) - When the answer was submitted
*/

// History records table (for all agent interactions)
/*
Table: history_records
Columns:
- id (UUID) - Primary key
- user_id (UUID) - Foreign key to auth.users
- session_id (UUID) - Nullable, foreign key to interview_sessions or other session tables
- timestamp (TIMESTAMP) - When the action occurred
- agent_name (TEXT) - Which agent was used ('resume', 'interview', 'contract', 'docs')
- action_type (TEXT) - Type of action performed
- summary_text (TEXT) - Brief summary of the action
- full_output (TEXT) - Full output/result of the action
*/

// Functions to create tables (SQL)
export const createTablesSQL = `
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create interview_sessions table
CREATE TABLE IF NOT EXISTS interview_sessions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  role TEXT,
  experience_level TEXT,
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,
  status TEXT DEFAULT 'in_progress',
  final_score INTEGER,
  overall_feedback TEXT,
  strengths JSONB,
  weaknesses JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create interview_questions table
CREATE TABLE IF NOT EXISTS interview_questions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  session_id UUID REFERENCES interview_sessions(id) ON DELETE CASCADE,
  question_number INTEGER,
  question_text TEXT,
  audio_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_answers table
CREATE TABLE IF NOT EXISTS user_answers (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  session_id UUID REFERENCES interview_sessions(id) ON DELETE CASCADE,
  question_id UUID REFERENCES interview_questions(id) ON DELETE CASCADE,
  answer_text TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create history_records table
CREATE TABLE IF NOT EXISTS history_records (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  session_id UUID,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  agent_name TEXT,
  action_type TEXT,
  summary_text TEXT,
  full_output TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_interview_sessions_user_id ON interview_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_interview_sessions_status ON interview_sessions(status);
CREATE INDEX IF NOT EXISTS idx_interview_questions_session_id ON interview_questions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_answers_session_id ON user_answers(session_id);
CREATE INDEX IF NOT EXISTS idx_history_records_user_id ON history_records(user_id);
CREATE INDEX IF NOT EXISTS idx_history_records_timestamp ON history_records(timestamp DESC);
`;

// Functions to insert data
export const insertInterviewSessionSQL = `
INSERT INTO interview_sessions (
  user_id, role, experience_level, status
) VALUES ($1, $2, $3, $4)
RETURNING id, started_at;
`;

export const updateInterviewSessionCompletionSQL = `
UPDATE interview_sessions 
SET 
  completed_at = NOW(),
  status = 'completed',
  final_score = $1,
  overall_feedback = $2,
  strengths = $3,
  weaknesses = $4,
  updated_at = NOW()
WHERE id = $5;
`;

export const insertInterviewQuestionSQL = `
INSERT INTO interview_questions (
  session_id, question_number, question_text, audio_url
) VALUES ($1, $2, $3, $4)
RETURNING id;
`;

export const insertUserAnswerSQL = `
INSERT INTO user_answers (
  session_id, question_id, answer_text
) VALUES ($1, $2, $3);
`;

export const insertHistoryRecordSQL = `
INSERT INTO history_records (
  user_id, session_id, agent_name, action_type, summary_text, full_output
) VALUES ($1, $2, $3, $4, $5, $6);
`;