import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

interface ChatMessage {
  id: string;
  type: 'ai' | 'user';
  content: string;
  timestamp: Date;
}

const InterviewSimulatorPage = () => {
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
  const [experienceLevel, setExperienceLevel] = useState('Intermediate');
  const [isListening, setIsListening] = useState(false);
  const [autoSubmitTimeout, setAutoSubmitTimeout] = useState<ReturnType<typeof setTimeout> | null>(null);
  
  const navigate = useNavigate();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Focus textarea when a new question is presented
    if (interviewStarted && currentQuestion && textareaRef.current) {
      textareaRef.current.focus();
    }
    
    // Initialize speech recognition
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false; // Change to false for auto-stop
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';
      
      recognitionRef.current.onresult = (event: any) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          }
        }
        
        if (finalTranscript) {
          setUserAnswer((prev) => prev + finalTranscript);
          
          // Clear any existing timeout
          if (autoSubmitTimeout) {
            clearTimeout(autoSubmitTimeout);
          }
          
          // Set a new timeout to auto-submit after 2 seconds of silence
          const timeout = setTimeout(() => {
            if (userAnswer.trim() || finalTranscript.trim()) {
              submitAnswer();
            }
          }, 2000);
          
          setAutoSubmitTimeout(timeout);
        }
      };
      
      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error', event.error);
        setIsListening(false);
        if (autoSubmitTimeout) {
          clearTimeout(autoSubmitTimeout);
        }
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
        // Auto-submit if we have content
        if (userAnswer.trim() && autoSubmitTimeout) {
          clearTimeout(autoSubmitTimeout);
          submitAnswer();
        }
      };
    }
    
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
  }, [interviewStarted, currentQuestion, userAnswer, autoSubmitTimeout]);

  const replayAudio = () => {
    if (audioRef.current) {
      audioRef.current.play();
      setIsPlayingAudio(true);
    }
  };

  const toggleListening = () => {
    if (!recognitionRef.current) {
      setError('Speech recognition is not supported in your browser.');
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
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const startInterview = async () => {
    setInterviewStarted(true);
    setIsLoading(true);
    setError(null);
    
    try {
      // Initial API call to start the interview
      const response = await fetch('http://localhost:8001/api/human_interview/start', {
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
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'continue') {
        setSessionId(data.session_id);
        setCurrentQuestion(data.question_text);
        
        // Add to chat history
        const aiMessage: ChatMessage = {
          id: `msg-${Date.now()}`,
          type: 'ai',
          content: data.question_text,
          timestamp: new Date()
        };
        
        setChatHistory([aiMessage]);
        
        // Play audio
        if (data.audio_url) {
          audioRef.current = new Audio(`http://localhost:8001${data.audio_url}`);
          audioRef.current.onended = () => setIsPlayingAudio(false);
          audioRef.current.play();
          setIsPlayingAudio(true);
        }
      } else {
        throw new Error('Failed to start interview');
      }
    } catch (err) {
      setError('Error: Interview session failed. Please try again.');
      console.error('Interview start error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const submitAnswer = async () => {
    if ((!userAnswer.trim() && !isListening) || !sessionId) return;
    
    // Stop listening if still active
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
    
    // Add user answer to chat history
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      type: 'user',
      content: userAnswer.trim() || '[Voice input submitted]',
      timestamp: new Date()
    };
    
    setChatHistory(prev => [...prev, userMessage]);
    
    // Clear the answer input
    setUserAnswer('');
    
    setIsLoading(true);
    setError(null);
    
    try {
      // API call to submit the answer and get the next question
      const response = await fetch('http://localhost:8001/api/human_interview/answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          answer_text: userAnswer.trim() || '[Voice input submitted]'
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'complete') {
        // Interview is complete
        setInterviewComplete(true);
        setFinalScore(data.final_score || 85);
        setOverallFeedback(data.overall_feedback || 'Great job! You demonstrated strong interview skills.');
        setStrengths(data.strengths || []);
        setWeaknesses(data.weaknesses || []);
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
        
        // Play audio
        if (data.audio_url) {
          audioRef.current = new Audio(`http://localhost:8001${data.audio_url}`);
          audioRef.current.onended = () => setIsPlayingAudio(false);
          audioRef.current.play();
          setIsPlayingAudio(true);
        }
      } else {
        throw new Error('Failed to get next question');
      }
    } catch (err) {
      setError('Error: Interview session failed. Please try again.');
      console.error('Submit answer error:', err);
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">Mock Interview Simulator</h1>
          <p className="text-gray-300">Practice with Sarah, our HR Specialist. Get real-time feedback and improve your interview skills!</p>
        </div>

        {!interviewStarted ? (
          <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-8 backdrop-blur-sm bg-opacity-90">
            <h2 className="text-3xl font-bold text-white mb-6 text-center">Setup Your Mock Interview</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div>
                <label htmlFor="role" className="block text-sm font-medium text-gray-300 mb-2">
                  Role
                </label>
                <input
                  type="text"
                  id="role"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-white placeholder-gray-400"
                  placeholder="e.g., Senior Data Analyst"
                />
              </div>
              
              <div>
                <label htmlFor="experienceLevel" className="block text-sm font-medium text-gray-300 mb-2">
                  Experience Level
                </label>
                <select
                  id="experienceLevel"
                  value={experienceLevel}
                  onChange={(e) => setExperienceLevel(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-white"
                >
                  <option value="Beginner" className="bg-gray-700">Beginner</option>
                  <option value="Intermediate" className="bg-gray-700">Intermediate</option>
                  <option value="Expert" className="bg-gray-700">Expert</option>
                </select>
              </div>
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={startInterview}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-lg font-semibold text-lg hover:from-blue-700 hover:to-indigo-800 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                Start Interview
              </button>
            </div>
          </div>
        ) : interviewComplete ? (
          <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-8 backdrop-blur-sm bg-opacity-90">
            <div className="text-center mb-8">
              <div className="w-24 h-24 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-white mb-2">Interview Complete!</h2>
              {finalScore && (
                <p className="text-2xl text-gray-300">Final Score: <span className="font-bold text-green-400">{finalScore}/100</span></p>
              )}
            </div>
            
            {overallFeedback && (
              <div className="mb-8 p-6 bg-gray-700 rounded-lg border border-gray-600">
                <h3 className="text-xl font-semibold text-white mb-3">Overall Feedback</h3>
                <p className="text-gray-300">{overallFeedback}</p>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {strengths.length > 0 && (
                <div className="p-6 bg-gradient-to-br from-green-900 to-emerald-900 rounded-lg border border-green-700">
                  <h3 className="text-xl font-semibold text-green-300 mb-3">Strengths</h3>
                  <ul className="space-y-2">
                    {strengths.map((strength, index) => (
                      <li key={index} className="flex items-start">
                        <div className="flex-shrink-0 mt-1">
                          <div className="w-5 h-5 rounded-full bg-green-800 flex items-center justify-center">
                            <svg className="w-3 h-3 text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                          </div>
                        </div>
                        <span className="ml-2 text-green-200">{strength}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {weaknesses.length > 0 && (
                <div className="p-6 bg-gradient-to-br from-amber-900 to-yellow-900 rounded-lg border border-amber-700">
                  <h3 className="text-xl font-semibold text-amber-300 mb-3">Areas for Improvement</h3>
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
                        <span className="ml-2 text-amber-200">{weakness}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            
            <div className="flex justify-center gap-4">
              <button
                onClick={handleReset}
                className="px-6 py-3 bg-gray-700 text-white rounded-lg font-medium hover:bg-gray-600 transition-colors border border-gray-600"
              >
                Try Another Interview
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-lg font-medium hover:from-blue-700 hover:to-indigo-800 transition-all"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-6 backdrop-blur-sm bg-opacity-90">
            {/* Chat history */}
            <div className="mb-6 max-h-96 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
              {chatHistory.map((message) => (
                <div 
                  key={message.id} 
                  className={`mb-6 ${message.type === 'ai' ? 'text-left' : 'text-right'}`}
                >
                  <div className="flex items-start">
                    {message.type === 'ai' && (
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center mr-3">
                        <span className="text-white text-sm font-bold">S</span>
                      </div>
                    )}
                    <div className="flex-1">
                      {message.type === 'ai' && (
                        <div className="text-xs text-gray-400 mb-1">Sarah, HR Specialist</div>
                      )}
                      <div 
                        className={`inline-block max-w-3/4 p-4 rounded-2xl ${
                          message.type === 'ai' 
                            ? 'bg-gray-700 text-white rounded-tl-none' 
                            : 'bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-tr-none'
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{message.content}</p>
                      </div>
                    </div>
                    {message.type === 'user' && (
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center ml-3">
                        <span className="text-white text-sm font-bold">Y</span>
                      </div>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-1 ml-13">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="mb-6 text-left">
                  <div className="flex items-start">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center mr-3">
                      <span className="text-white text-sm font-bold">S</span>
                    </div>
                    <div className="flex-1">
                      <div className="text-xs text-gray-400 mb-1">Sarah, HR Specialist</div>
                      <div className="inline-block bg-gray-700 text-white p-4 rounded-2xl rounded-tl-none">
                        <div className="flex items-center">
                          <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white mr-3"></div>
                          <span>{isPlayingAudio ? "Speaking..." : "Thinking..."}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {/* Current question with speaker */}
            {currentQuestion && !isLoading && (
              <div className="mb-6 p-4 bg-gradient-to-r from-gray-700 to-gray-800 text-white rounded-2xl border border-gray-600">
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center mr-3">
                    <span className="text-white text-sm font-bold">S</span>
                  </div>
                  <div className="flex-1">
                    <div className="text-xs text-gray-400 mb-1">Sarah, HR Specialist</div>
                    <p className="mb-3 text-lg">{currentQuestion}</p>
                  </div>
                  <button 
                    onClick={replayAudio}
                    disabled={isPlayingAudio}
                    className="ml-4 p-2 bg-gray-600 rounded-full hover:bg-gray-500 transition-colors disabled:opacity-50"
                    aria-label="Replay audio"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 001.414 1.414m-2.828-9.9a9 9 0 012.828-2.828"></path>
                    </svg>
                  </button>
                </div>
              </div>
            )}
            
            {/* Error message */}
            {error && (
              <div className="mb-6 p-4 bg-red-900 border border-red-700 rounded-lg">
                <p className="text-red-200">{error}</p>
              </div>
            )}
            
            {/* User input area */}
            <div className="mb-6">
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
                  placeholder="Type your answer here or use the microphone..."
                  rows={4}
                  className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-l-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-white placeholder-gray-400 resize-none"
                  disabled={isLoading || isListening}
                />
                <button
                  onClick={toggleListening}
                  disabled={isLoading}
                  className={`px-4 rounded-r-lg flex items-center justify-center ${
                    isListening 
                      ? 'bg-red-600 hover:bg-red-700 text-white' 
                      : 'bg-gray-600 hover:bg-gray-500 text-white'
                  } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                  aria-label={isListening ? "Stop listening" : "Start voice input"}
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                  </svg>
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {isListening ? "Listening... Speak now" : "Press Enter to submit, Shift+Enter for new line, or use the mic for voice input"}
              </p>
            </div>
            
            <div className="flex justify-end">
              <button
                onClick={submitAnswer}
                disabled={isLoading || (!userAnswer.trim() && !isListening)}
                className={`px-6 py-3 rounded-lg font-medium transition-all ${
                  isLoading || (!userAnswer.trim() && !isListening)
                    ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-600 to-indigo-700 text-white hover:from-blue-700 hover:to-indigo-800 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                }`}
              >
                Submit Answer
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InterviewSimulatorPage;