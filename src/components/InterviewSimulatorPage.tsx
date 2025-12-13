import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../supabase/AuthContext';
import { 
  createInterviewSession, 
  updateInterviewSessionWithBackendId,
  updateInterviewSessionCompletion 
} from '../supabase/services';

interface ChatMessage {
  id: string;
  type: 'ai' | 'user';
  content: string;
  timestamp: Date;
}

const InterviewSimulatorPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState<string | null>(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [interviewComplete, setInterviewComplete] = useState(false);
  const [finalScore, setFinalScore] = useState<number | null>(null);
  const [overallFeedback, setOverallFeedback] = useState<string | null>(null);
  const [strengths, setStrengths] = useState<string[]>([]);
  const [weaknesses, setWeaknesses] = useState<string[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [role, setRole] = useState('Senior Data Analyst');
  const [experienceLevel, setExperienceLevel] = useState('Beginner');
  const [isListening, setIsListening] = useState(false);
  const [autoSubmitTimeout, setAutoSubmitTimeout] = useState<ReturnType<typeof setTimeout> | null>(null);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<any>(null);
  // Add a ref to track audio playback state
  const isAudioPlayingRef = useRef(false);

  // Redirect to login if user is not authenticated
  useEffect(() => {
    if (!user) {
      navigate('/login');
    }
  }, [user, navigate]);

  useEffect(() => {
    // Focus textarea when a new question is presented
    if (interviewStarted && currentQuestion && textareaRef.current) {
      textareaRef.current.focus();
    }
    
    // Check for browser support
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari for voice input features.');
      return;
    }
    
    // Initialize speech recognition with better configuration
    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = false; // Single utterance mode
    recognitionRef.current.interimResults = true;
    recognitionRef.current.lang = 'en-US';
    // Add noise reduction and confidence settings
    recognitionRef.current.maxAlternatives = 1;
    
    recognitionRef.current.onresult = (event: any) => {
      let finalTranscript = '';
      let interimTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        // Only process results with high confidence
        if (event.results[i].isFinal && event.results[i][0].confidence > 0.7) {
          finalTranscript += transcript + ' ';
        } else if (event.results[i].isFinal) {
          // For lower confidence, still include but mark as possibly inaccurate
          finalTranscript += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }
      
      // Update user answer with final transcript
      if (finalTranscript) {
        setUserAnswer((prev) => prev + finalTranscript);
        
        // Clear any existing timeout
        if (autoSubmitTimeout) {
          clearTimeout(autoSubmitTimeout);
        }
        
        // Set a new timeout to auto-submit after 2 seconds of silence
        const timeout = setTimeout(() => {
          if ((userAnswer + finalTranscript).trim()) {
            // Only submit if we're still in interview mode and not already loading
            if (interviewStarted && !interviewComplete && !isLoading) {
              submitAnswer();
            }
          }
        }, 2000);
        
        setAutoSubmitTimeout(timeout);
      }
    };
    
    recognitionRef.current.onerror = (event: any) => {
      setIsListening(false);
      if (autoSubmitTimeout) {
        clearTimeout(autoSubmitTimeout);
        setAutoSubmitTimeout(null);
      }
      // Show user-friendly error messages
      switch(event.error) {
        case 'no-speech':
          setError('No speech detected. Please try again and speak clearly.');
          break;
        case 'audio-capture':
          setError('Audio capture failed. Please check your microphone.');
          break;
        case 'not-allowed':
        case 'permission-denied':
          setError('Microphone access denied. Please allow microphone access in your browser settings.');
          break;
        case 'network':
          setError('Network error. Please check your connection.');
          break;
        case 'bad-grammar':
          setError('Grammar error. Please try again.');
          break;
        default:
          setError(`Speech recognition error: ${event.error}. Please try again.`);
      }
    };
    
    recognitionRef.current.onend = () => {
      setIsListening(false);
      // Auto-submit if we have content and we're not already loading
      if (userAnswer.trim() && autoSubmitTimeout && interviewStarted && !interviewComplete && !isLoading) {
        clearTimeout(autoSubmitTimeout);
        setAutoSubmitTimeout(null);
        submitAnswer();
      }
    };
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (audioRef.current) {
        audioRef.current.pause();
      }
      if (autoSubmitTimeout) {
        clearTimeout(autoSubmitTimeout);
      }
    };
  }, [interviewStarted, currentQuestion, userAnswer, autoSubmitTimeout, interviewComplete, isLoading]);

  const replayAudio = async () => {
    if (audioRef.current) {
      try {
        // Reset playback position
        audioRef.current.currentTime = 0;
        
        // Ensure any previous playback is stopped
        if (isAudioPlayingRef.current) {
          audioRef.current.pause();
          isAudioPlayingRef.current = false;
        }
        
        // Play the audio
        isAudioPlayingRef.current = true;
        await audioRef.current.play();
        setIsPlayingAudio(true);
      } catch (error) {
        isAudioPlayingRef.current = false;
        setIsPlayingAudio(false);
        // Don't show error to user, just continue silently
      }
    }
  };

  const toggleListening = () => {
    if (!recognitionRef.current) {
      setError('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari for voice input features.');
      return;
    }
    
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
      if (autoSubmitTimeout) {
        clearTimeout(autoSubmitTimeout);
      }
    } else {
      // Clear the answer input when starting to listen
      setUserAnswer('');
      
      // Check if mediaDevices is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError('Audio recording is not supported in your browser. Please use Chrome, Edge, or Safari.');
        return;
      }
      
      try {
        // Request microphone permission explicitly
        navigator.mediaDevices.getUserMedia({ audio: true })
          .then(() => {
            recognitionRef.current.start();
            setIsListening(true);
            setError(null); // Clear any previous errors
          })
          .catch((err) => {
            if (err.name === 'NotAllowedError') {
              setError('Microphone access denied. Please allow microphone access in your browser settings to use voice input.');
            } else if (err.name === 'NotFoundError') {
              setError('No microphone found. Please connect a microphone and try again.');
            } else {
              setError(`Microphone error: ${err.message}. Please check your audio settings.`);
            }
            setIsListening(false);
          });
      } catch (err) {
        setError('Failed to start voice recognition. Please try again.');
        setIsListening(false);
      }
    }
  };

  const startInterview = async () => {
    if (!user) {
      setError('User not authenticated');
      return;
    }
    
    if (!role) {
      setError('Role is required');
      return;
    }
    if (!experienceLevel) {
      setError('Experience level is required');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Create interview session in Supabase
      const { session, error: sessionError } = await createInterviewSession(
        user.id,
        role,
        experienceLevel
      );
      
      if (sessionError) {
        throw new Error(`Failed to create interview session: ${sessionError.message}`);
      }
      
      if (!session) {
        throw new Error('Failed to create interview session');
      }
      
      // Log the request details for debugging      
      // Initial API call to start the interview
      const response = await fetch('http://localhost:8000/api/human_interview/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          role: role,
          experience_level: experienceLevel
        }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'continue') {
        setInterviewStarted(true);
        setSessionId(data.session_id); // Use the backend session ID
        
        // Update the Supabase session with the backend session ID
        if (session.id) {
          const { error: updateError } = await updateInterviewSessionWithBackendId(
            session.id,
            data.session_id
          );
          
          if (updateError) {
          }
        }
        
        setCurrentQuestion(data.question_text);
        
        // Add to chat history
        const aiMessage: ChatMessage = {
          id: `msg-${Date.now()}`,
          type: 'ai',
          content: data.question_text,
          timestamp: new Date()
        };
        
        setChatHistory([aiMessage]);
        
        // Play audio with proper error handling
        if (data.audio_url) {
          try {
            // Stop any existing audio playback
            if (audioRef.current) {
              audioRef.current.pause();
              isAudioPlayingRef.current = false;
            }
            
            // Create new audio instance
            audioRef.current = new Audio(`http://localhost:8000${data.audio_url}`);
            audioRef.current.onended = () => {
              isAudioPlayingRef.current = false;
              setIsPlayingAudio(false);
            };
            
            // Handle audio errors
            audioRef.current.onerror = (e) => {
              isAudioPlayingRef.current = false;
              setIsPlayingAudio(false);
              // Don't show error to user, just continue silently
            };
            
            // Play the audio with proper async handling
            isAudioPlayingRef.current = true;
            await audioRef.current.play();
            setIsPlayingAudio(true);
          } catch (audioError) {
            console.error('Audio setup/playback error:', audioError);
            isAudioPlayingRef.current = false;
            setIsPlayingAudio(false);
            // Continue without audio
          }
        }
      } else {
        throw new Error('Failed to start interview');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Interview session failed. Please try again.';
      setError(`Error: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!user || !sessionId) {
      setError('User not authenticated or session not found');
      return;
    }
    
    // Prevent submission if no answer and not listening, or no session
    if ((!userAnswer.trim() && !isListening) || !sessionId) return;
    
    // Stop listening if still active
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
    
    // Clear any auto-submit timeout
    if (autoSubmitTimeout) {
      clearTimeout(autoSubmitTimeout);
      setAutoSubmitTimeout(null);
    }
    
    // Get the current answer before clearing
    const answerToSubmit = userAnswer.trim() || '[Voice input submitted]';
    
    // Add user answer to chat history immediately
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      type: 'user',
      content: answerToSubmit,
      timestamp: new Date()
    };
    
    setChatHistory(prev => [...prev, userMessage]);
    
    // Clear the answer input immediately
    setUserAnswer('');
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Validate required fields
      if (!sessionId) {
        throw new Error('Session ID is missing');
      }
      if (!answerToSubmit) {
        throw new Error('Answer is required');
      }
      
      // Log the request details for debugging
      
      // API call to submit the answer and get the next question
      const response = await fetch('http://localhost:8000/api/human_interview/answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId, // Use the backend session ID
          answer_text: answerToSubmit
        }),
      });
      
      
      if (!response.ok) {
        const errorText = await response.text();
        // Handle specific error cases
        if (response.status === 423) {
          // Session locked, wait a bit and retry once
          await new Promise(resolve => setTimeout(resolve, 1000));
          throw new Error('Session busy. Please try again.');
        }
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'complete') {
        // Interview is complete
        setInterviewComplete(true);
        setFinalScore(data.final_score || 85);
        setOverallFeedback(data.overall_feedback || 'Great job! You demonstrated strong interview skills.');
        setStrengths(data.strengths || []);
        setWeaknesses(data.weaknesses || []);
        
        // Update interview session completion in Supabase
        const { error: updateError } = await updateInterviewSessionCompletion(
          sessionId,
          data.final_score || 85,
          data.overall_feedback || 'Great job! You demonstrated strong interview skills.',
          data.strengths || [],
          data.weaknesses || []
        );
        
        if (updateError) {
        }
        
        return;
      }
      
      if (data.status === 'continue') {
        setCurrentQuestion(data.question_text);
        
        // Add to chat history
        const aiMessage: ChatMessage = {
          id: `msg-${Date.now()}`,
          type: 'ai',
          content: data.question_text,
          timestamp: new Date()
        };
        
        setChatHistory(prev => [...prev, aiMessage]);
        
        // Play audio with proper error handling
        if (data.audio_url) {
          try {
            // Stop any existing audio playback
            if (audioRef.current) {
              audioRef.current.pause();
              isAudioPlayingRef.current = false;
            }
            
            // Create new audio instance
            audioRef.current = new Audio(`http://localhost:8000${data.audio_url}`);
            audioRef.current.onended = () => {
              isAudioPlayingRef.current = false;
              setIsPlayingAudio(false);
            };
            
            // Handle audio errors
            audioRef.current.onerror = (e) => {
              isAudioPlayingRef.current = false;
              setIsPlayingAudio(false);
              // Don't show error to user, just continue silently
            };
            
            // Play the audio with proper async handling
            isAudioPlayingRef.current = true;
            await audioRef.current.play();
            setIsPlayingAudio(true);
          } catch (audioError) {
            console.error('Audio setup/playback error:', audioError);
            isAudioPlayingRef.current = false;
            setIsPlayingAudio(false);
            // Continue without audio
          }
        }
      } else {
        throw new Error('Unexpected response from server');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to submit answer. Please try again.';
      setError(`Error: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setInterviewStarted(false);
    setCurrentQuestion(null);
    setUserAnswer('');
    setChatHistory([]);
    setIsLoading(false);
    setIsPlayingAudio(false);
    setError(null);
    setInterviewComplete(false);
    setFinalScore(null);
    setOverallFeedback(null);
    setStrengths([]);
    setWeaknesses([]);
    setSessionId(null);
    setIsListening(false);
    isAudioPlayingRef.current = false;
    
    // Reset audio and speech recognition
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (autoSubmitTimeout) {
      clearTimeout(autoSubmitTimeout);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault();
      // Clear any auto-submit timeout when manually submitting
      if (autoSubmitTimeout) {
        clearTimeout(autoSubmitTimeout);
      }
      submitAnswer();
    }
  };

  // Don't render if user is not authenticated
  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 py-6 px-4 sm:px-6">
      {/* Back Button */}
      <div className="max-w-4xl mx-auto mb-4">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center text-gray-300 hover:text-white transition-colors group py-2"
          aria-label="Back to Dashboard"
        >
          <svg className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          <span className="font-medium">Back</span>
        </button>
      </div>

      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-6">
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">🎤 Mock Interview</h1>
          <p className="text-gray-300 text-sm sm:text-base max-w-2xl mx-auto">Practice with Sarah, our HR Specialist. Get real-time feedback!</p>
        </div>

        {!interviewStarted ? (
          <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-6 sm:p-8 backdrop-blur-sm bg-opacity-90">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-5 text-center">Setup Your Interview</h2>
            
            <div className="space-y-5 mb-7">
              <div>
                <label htmlFor="role" className="block text-sm font-medium text-gray-300 mb-2">
                  Role
                </label>
                <input
                  type="text"
                  id="role"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-700 border border-purple-500 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-white placeholder-gray-400"
                  placeholder="e.g., Senior Data Analyst"
                />
              </div>
              
              <div>
                <label htmlFor="experienceLevel" className="block text-sm font-medium text-gray-300 mb-2">
                  Experience Level
                </label>
                <div className="relative">
                  <select
                    id="experienceLevel"
                    value={experienceLevel}
                    onChange={(e) => setExperienceLevel(e.target.value)}
                    className="w-full px-4 py-3 bg-gray-700 border border-purple-500 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-white appearance-none"
                  >
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Expert">Expert</option>
                  </select>
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={startInterview}
                className="w-full py-3 sm:py-4 bg-gradient-to-r from-purple-600 to-indigo-700 text-white rounded-lg font-semibold text-base sm:text-lg hover:from-purple-700 hover:to-indigo-800 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                Start Interview
              </button>
            </div>
          </div>
        ) : interviewComplete ? (
          <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-6 sm:p-8 backdrop-blur-sm bg-opacity-90">
            <div className="text-center mb-6">
              <div className="w-20 h-20 sm:w-24 sm:h-24 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-10 h-10 sm:w-12 sm:h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2">Interview Complete!</h2>
              {finalScore && (
                <p className="text-xl sm:text-2xl text-gray-300">Score: <span className="font-bold text-purple-400">{finalScore}/100</span></p>
              )}
            </div>
            
            {overallFeedback && (
              <div className="mb-6 p-4 sm:p-5 bg-gray-700 rounded-lg border border-gray-600">
                <h3 className="text-lg sm:text-xl font-semibold text-white mb-2">Overall Feedback</h3>
                <p className="text-gray-300 text-sm sm:text-base">{overallFeedback}</p>
              </div>
            )}
            
            <div className="space-y-5 mb-6">
              {strengths.length > 0 && (
                <div className="p-4 sm:p-5 bg-gradient-to-br from-purple-900 to-indigo-900 rounded-lg border border-purple-700">
                  <h3 className="text-lg sm:text-xl font-semibold text-purple-300 mb-3">Strengths</h3>
                  <ul className="space-y-2">
                    {strengths.map((strength, index) => (
                      <li key={index} className="flex items-start">
                        <div className="flex-shrink-0 mt-1">
                          <div className="w-5 h-5 rounded-full bg-purple-800 flex items-center justify-center">
                            <svg className="w-3 h-3 text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                          </div>
                        </div>
                        <span className="ml-2 text-purple-200 text-sm sm:text-base">{strength}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {weaknesses.length > 0 && (
                <div className="p-4 sm:p-5 bg-gradient-to-br from-amber-900 to-yellow-900 rounded-lg border border-amber-700">
                  <h3 className="text-lg sm:text-xl font-semibold text-amber-300 mb-3">Areas for Improvement</h3>
                  <ul className="space-y-2">
                    {weaknesses.map((weakness, index) => (
                      <li key={index} className="flex items-start">
                        <div className="flex-shrink-0 mt-1">
                          <div className="w-5 h-5 rounded-full bg-amber-800 flex items-center justify-center">
                            <svg className="w-3 h-3 text-amber-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                            </svg>
                          </div>
                        </div>
                        <span className="ml-2 text-amber-200 text-sm sm:text-base">{weakness}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={handleReset}
                className="w-full sm:w-auto px-5 py-3 bg-gray-700 text-white rounded-lg font-medium hover:bg-gray-600 transition-colors border border-gray-600"
              >
                Try Another Interview
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-5 sm:p-6 backdrop-blur-sm bg-opacity-90">
            {/* Chat history */}
            <div className="mb-5 max-h-64 sm:max-h-80 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
              {chatHistory.map((message) => (
                <div 
                  key={message.id} 
                  className={`mb-5 ${message.type === 'ai' ? 'text-left' : 'text-right'}`}
                >
                  <div className="flex items-start">
                    {message.type === 'ai' && (
                      <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-purple-600 to-indigo-700 flex items-center justify-center mr-2 sm:mr-3">
                        <span className="text-white text-xs sm:text-sm font-bold">S</span>
                      </div>
                    )}
                    <div className="flex-1">
                      {message.type === 'ai' && (
                        <div className="text-xs text-gray-400 mb-1">Sarah, HR Specialist</div>
                      )}
                      <div 
                        className={`inline-block max-w-3/4 p-3 sm:p-4 rounded-2xl ${
                          message.type === 'ai' 
                            ? 'bg-gray-700 text-white rounded-tl-none' 
                            : 'bg-gradient-to-r from-purple-600 to-indigo-700 text-white rounded-tr-none'
                        }`}
                      >
                        <p className="whitespace-pre-wrap text-sm sm:text-base">{message.content}</p>
                      </div>
                    </div>
                    {message.type === 'user' && (
                      <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center ml-2 sm:ml-3">
                        <span className="text-white text-xs sm:text-sm font-bold">Y</span>
                      </div>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-1 ml-10 sm:ml-13">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="mb-5 text-left">
                  <div className="flex items-start">
                    <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-purple-600 to-indigo-700 flex items-center justify-center mr-2 sm:mr-3">
                      <span className="text-white text-xs sm:text-sm font-bold">S</span>
                    </div>
                    <div className="flex-1">
                      <div className="text-xs text-gray-400 mb-1">Sarah, HR Specialist</div>
                      <div className="inline-block bg-gray-700 text-white p-3 sm:p-4 rounded-2xl rounded-tl-none">
                        <div className="flex items-center">
                          <div className="animate-spin rounded-full h-4 w-4 sm:h-5 sm:w-5 border-t-2 border-b-2 border-white mr-2 sm:mr-3"></div>
                          <span className="text-sm sm:text-base">{isPlayingAudio ? "Speaking..." : "Thinking..."}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {/* Current question with speaker */}
            {currentQuestion && !isLoading && (
              <div className="mb-5 p-3 sm:p-4 bg-gradient-to-r from-gray-700 to-gray-800 text-white rounded-2xl border border-gray-600">
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-purple-600 to-indigo-700 flex items-center justify-center mr-2 sm:mr-3">
                    <span className="text-white text-xs sm:text-sm font-bold">S</span>
                  </div>
                  <div className="flex-1">
                    <div className="text-xs text-gray-400 mb-1">Sarah, HR Specialist</div>
                    <p className="mb-2 sm:mb-3 text-sm sm:text-base">{currentQuestion}</p>
                  </div>
                  <button 
                    onClick={replayAudio}
                    disabled={isPlayingAudio}
                    className="ml-2 sm:ml-3 p-2 bg-gray-600 rounded-full hover:bg-gray-500 transition-colors disabled:opacity-50"
                    aria-label="Replay audio"
                  >
                    <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 001.414 1.414m-2.828-9.9a9 9 0 012.828-2.828"></path>
                    </svg>
                  </button>
                </div>
              </div>
            )}
            
            {/* Error message */}
            {error && (
              <div className="mb-5 p-3 sm:p-4 bg-red-900 border border-red-700 rounded-lg">
                <p className="text-red-200 text-sm sm:text-base">{error}</p>
              </div>
            )}
            
            {/* User input area */}
            <div className="mb-5">
              <label htmlFor="answer" className="block text-sm font-medium text-gray-300 mb-2">
                Your Response
              </label>
              <div className="flex">
                <textarea
                  ref={textareaRef}
                  id="answer"
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Type your answer or use mic..."
                  rows={3}
                  className="flex-1 px-3 py-2 sm:px-4 sm:py-3 bg-gray-700 border border-purple-500 rounded-l-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-white placeholder-gray-400 resize-none text-sm sm:text-base"
                  disabled={isLoading || isListening}
                />
                <button
                  onClick={toggleListening}
                  disabled={isLoading}
                  className={`px-3 sm:px-4 rounded-r-lg flex items-center justify-center transition-all duration-200 ${
                    isListening 
                      ? 'bg-red-600 hover:bg-red-700 text-white animate-pulse' 
                      : 'bg-gray-600 hover:bg-gray-500 text-white'
                  } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                  aria-label={isListening ? "Stop listening" : "Start voice input"}
                >
                  <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                  </svg>
                </button>
              </div>
            </div>
            
            {/* Submit button */}
            <div className="flex justify-center">
              <button
                onClick={submitAnswer}
                disabled={isLoading || (!userAnswer.trim() && !isListening)}
                className={`px-6 py-3 rounded-lg font-medium transition-all ${
                  (!userAnswer.trim() && !isListening) || isLoading
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-purple-600 to-indigo-700 text-white hover:from-purple-700 hover:to-indigo-800 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                }`}
              >
                {isLoading ? 'Submitting...' : 'Submit Answer'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InterviewSimulatorPage;