import { supabase } from './client';
import { User } from '@supabase/supabase-js';

// Interview Session Types
export interface InterviewSession {
  id: string;
  user_id: string;
  role: string;
  experience_level: string;
  started_at: string;
  completed_at: string | null;
  status: 'in_progress' | 'completed' | 'cancelled';
  final_score: number | null;
  overall_feedback: string | null;
  strengths: string[] | null;
  weaknesses: string[] | null;
  created_at: string;
  updated_at: string;
}

// Interview Question Types
export interface InterviewQuestion {
  id: string;
  session_id: string;
  question_number: number;
  question_text: string;
  audio_url: string | null;
  created_at: string;
}

// User Answer Types
export interface UserAnswer {
  id: string;
  session_id: string;
  question_id: string;
  answer_text: string;
  created_at: string;
}

// History Record Types
export interface HistoryRecord {
  id: string;
  user_id: string;
  session_id: string | null;
  timestamp: string;
  agent_name: string;
  action_type: string;
  summary_text: string;
  full_output: string;
}

// Add a map to store the relationship between Supabase session IDs and backend session IDs
const sessionMap = new Map<string, string>(); // supabaseId -> backendId
const reverseSessionMap = new Map<string, string>(); // backendId -> supabaseId

// Interview Session Services
export const createInterviewSession = async (
  userId: string,
  role: string,
  experienceLevel: string
): Promise<{ session: InterviewSession | null; error: Error | null }> => {
  try {
    const { data, error } = await supabase
      .from('interview_sessions')
      .insert([
        {
          user_id: userId,
          role,
          experience_level: experienceLevel,
          status: 'in_progress'
        }
      ])
      .select()
      .single();

    if (error) throw error;
    return { session: data, error: null };
  } catch (error: any) {
    return { session: null, error };
  }
};

export const updateInterviewSessionWithBackendId = async (
  supabaseSessionId: string,
  backendSessionId: string
): Promise<{ error: Error | null }> => {
  try {
    // Store the mapping in both directions
    sessionMap.set(supabaseSessionId, backendSessionId);
    reverseSessionMap.set(backendSessionId, supabaseSessionId);
    
    // Update the Supabase session with the backend session ID
    const { error } = await supabase
      .from('interview_sessions')
      .update({
        updated_at: new Date().toISOString()
      })
      .eq('id', supabaseSessionId);

    if (error) throw error;
    return { error: null };
  } catch (error: any) {
    return { error };
  }
};

export const updateInterviewSessionCompletion = async (
  sessionId: string, // This will be the backend session ID
  finalScore: number,
  overallFeedback: string,
  strengths: string[],
  weaknesses: string[]
): Promise<{ error: Error | null }> => {
  try {
    // Find the Supabase session ID that maps to this backend session ID
    let supabaseSessionId = reverseSessionMap.get(sessionId);
    
    if (!supabaseSessionId) {
      // If we can't find the mapping, try to update any session with the given ID
      supabaseSessionId = sessionId;
    }
    
    const { error } = await supabase
      .from('interview_sessions')
      .update({
        completed_at: new Date().toISOString(),
        status: 'completed',
        final_score: finalScore,
        overall_feedback: overallFeedback,
        strengths: strengths,
        weaknesses: weaknesses,
        updated_at: new Date().toISOString()
      })
      .eq('id', supabaseSessionId);

    if (error) throw error;
    
    // Remove the mapping as the session is now complete
    if (supabaseSessionId !== sessionId) {
      sessionMap.delete(supabaseSessionId);
      reverseSessionMap.delete(sessionId);
    }
    
    return { error: null };
  } catch (error: any) {
    return { error };
  }
};

// Interview Question Services
export const createInterviewQuestion = async (
  sessionId: string,
  questionNumber: number,
  questionText: string,
  audioUrl: string | null = null
): Promise<{ question: InterviewQuestion | null; error: Error | null }> => {
  try {
    const { data, error } = await supabase
      .from('interview_questions')
      .insert([
        {
          session_id: sessionId,
          question_number: questionNumber,
          question_text: questionText,
          audio_url: audioUrl
        }
      ])
      .select()
      .single();

    if (error) throw error;
    return { question: data, error: null };
  } catch (error: any) {
    return { question: null, error };
  }
};

// User Answer Services
export const createUserAnswer = async (
  sessionId: string,
  questionId: string,
  answerText: string
): Promise<{ error: Error | null }> => {
  try {
    const { error } = await supabase
      .from('user_answers')
      .insert([
        {
          session_id: sessionId,
          question_id: questionId,
          answer_text: answerText
        }
      ]);

    if (error) throw error;
    return { error: null };
  } catch (error: any) {
    return { error };
  }
};

// History Record Services
export const createHistoryRecord = async (
  userId: string,
  sessionId: string | null,
  agentName: string,
  actionType: string,
  summaryText: string,
  fullOutput: string
): Promise<{ record: HistoryRecord | null; error: Error | null }> => {
  try {
    const { data, error } = await supabase
      .from('history_records')
      .insert([
        {
          user_id: userId,
          session_id: sessionId,
          agent_name: agentName,
          action_type: actionType,
          summary_text: summaryText,
          full_output: fullOutput
        }
      ])
      .select()
      .single();

    if (error) throw error;
    return { record: data, error: null };
  } catch (error: any) {
    return { record: null, error };
  }
};

export const getUserHistory = async (
  userId: string,
  page: number = 1,
  limit: number = 20
): Promise<{ records: HistoryRecord[] | null; totalCount: number; error: Error | null }> => {
  try {
    // Get total count
    const { count, error: countError } = await supabase
      .from('history_records')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', userId);

    if (countError) throw countError;

    // Get paginated records
    const { data, error } = await supabase
      .from('history_records')
      .select('*')
      .eq('user_id', userId)
      .order('timestamp', { ascending: false })
      .range((page - 1) * limit, page * limit - 1);

    if (error) throw error;
    return { records: data, totalCount: count || 0, error: null };
  } catch (error: any) {
    return { records: null, totalCount: 0, error };
  }
};

// Get interview session with questions and answers
export const getInterviewSessionDetails = async (
  sessionId: string
): Promise<{ 
  session: InterviewSession | null; 
  questions: InterviewQuestion[] | null; 
  answers: UserAnswer[] | null; 
  error: Error | null 
}> => {
  try {
    // Get session
    const { data: session, error: sessionError } = await supabase
      .from('interview_sessions')
      .select('*')
      .eq('id', sessionId)
      .single();

    if (sessionError) throw sessionError;

    // Get questions
    const { data: questions, error: questionsError } = await supabase
      .from('interview_questions')
      .select('*')
      .eq('session_id', sessionId)
      .order('question_number', { ascending: true });

    if (questionsError) throw questionsError;

    // Get answers
    const { data: answers, error: answersError } = await supabase
      .from('user_answers')
      .select('*')
      .eq('session_id', sessionId);

    if (answersError) throw answersError;

    return { 
      session, 
      questions, 
      answers, 
      error: null 
    };
  } catch (error: any) {
    return { 
      session: null, 
      questions: null, 
      answers: null, 
      error 
    };
  }
};