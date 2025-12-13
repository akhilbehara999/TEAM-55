import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../supabase/AuthContext';
import { getUserHistory, getInterviewSessionDetails } from '../supabase/services';

interface HistoryRecord {
  id: string;
  user_id: string;
  session_id: string | null;
  timestamp: string;
  agent_name: string;
  summary_text: string;
  full_output: string;
  action_type: string;
}

const HistoryPage: React.FC = () => {
  const [historyData, setHistoryData] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [recordsPerPage] = useState(20);
  const [selectedRecord, setSelectedRecord] = useState<HistoryRecord | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [modalData, setModalData] = useState<any>(null);
  
  const navigate = useNavigate();
  const { user } = useAuth();

  // Redirect to login if user is not authenticated
  useEffect(() => {
    if (!user) {
      navigate('/login');
    }
  }, [user, navigate]);

  useEffect(() => {
    if (user) {
      fetchHistoryData();
    }
  }, [user, currentPage]);

  const fetchHistoryData = async () => {
    if (!user) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const { records, totalCount, error: fetchError } = await getUserHistory(
        user.id,
        currentPage,
        recordsPerPage
      );
      
      if (fetchError) {
        throw new Error(fetchError.message || 'Failed to fetch history data');
      }
      
      if (records) {
        setHistoryData(records);
        setTotalRecords(totalCount);
      }
    } catch (err: any) {
      setError('Failed to load history data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (record: HistoryRecord) => {
    setSelectedRecord(record);
    setIsModalOpen(true);
    setModalLoading(true);
    setModalData(null);
    
    try {
      // If this is an interview session, fetch the detailed data
      if (record.agent_name === 'interview' && record.session_id) {
        const { session, questions, answers, error: sessionError } = await getInterviewSessionDetails(record.session_id);
        
        if (sessionError) {
          throw new Error(sessionError.message || 'Failed to fetch session details');
        }
        
        setModalData({
          session,
          questions,
          answers
        });
      } else {
        // For other agents, just show the full output
        setModalData({
          full_output: record.full_output
        });
      }
    } catch (err: any) {
      setError('Failed to load details. Please try again.');
    } finally {
      setModalLoading(false);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedRecord(null);
    setModalData(null);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const totalPages = Math.ceil(totalRecords / recordsPerPage);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  // Don't render if user is not authenticated
  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 py-6 px-4 sm:px-6">
      {/* Back Button */}
      <div className="max-w-6xl mx-auto mb-6">
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

      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">📜 History</h1>
          <p className="text-gray-300 text-sm sm:text-base max-w-2xl mx-auto">
            View all actions performed across your agents
          </p>
        </div>

        {/* History Table */}
        <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-4 sm:p-6 backdrop-blur-sm bg-opacity-90">
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-green-500"></div>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <div className="text-red-400 mb-4">{error}</div>
              <button
                onClick={fetchHistoryData}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Retry
              </button>
            </div>
          ) : historyData.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-2">No history records found</div>
              <div className="text-gray-500 text-sm">Perform actions with the agents to see history here</div>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700">
                  <thead>
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Date/Time</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Agent Used</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Result/Status</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {historyData.map((record) => (
                      <tr key={record.id} className="hover:bg-gray-750 transition-colors">
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-300">
                          {formatDate(record.timestamp)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-white">
                          {record.agent_name}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-300">
                          {record.summary_text}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm">
                          <button
                            onClick={() => handleViewDetails(record)}
                            className="px-3 py-1 bg-gray-700 text-gray-300 rounded-md hover:bg-gray-600 transition-colors text-xs"
                          >
                            View Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalRecords > recordsPerPage && (
                <div className="flex items-center justify-between mt-6">
                  <div className="text-sm text-gray-400">
                    Showing {(currentPage - 1) * recordsPerPage + 1} to {Math.min(currentPage * recordsPerPage, totalRecords)} of {totalRecords} records
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                      className={`px-3 py-1 rounded-md text-sm ${
                        currentPage === 1 
                          ? 'bg-gray-700 text-gray-500 cursor-not-allowed' 
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      Previous
                    </button>
                    
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum;
                      if (totalPages <= 5) {
                        pageNum = i + 1;
                      } else if (currentPage <= 3) {
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                      } else {
                        pageNum = currentPage - 2 + i;
                      }
                      
                      return (
                        <button
                          key={pageNum}
                          onClick={() => handlePageChange(pageNum)}
                          className={`px-3 py-1 rounded-md text-sm ${
                            currentPage === pageNum
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                          }`}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                    
                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className={`px-3 py-1 rounded-md text-sm ${
                        currentPage === totalPages
                          ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Modal for viewing details */}
      {isModalOpen && selectedRecord && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold text-white">Details</h3>
              <button
                onClick={closeModal}
                className="text-gray-400 hover:text-white"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            {modalLoading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
              </div>
            ) : modalData ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Agent:</span>
                    <span className="text-white ml-2">{selectedRecord.agent_name}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Date/Time:</span>
                    <span className="text-white ml-2">{formatDate(selectedRecord.timestamp)}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Action:</span>
                    <span className="text-white ml-2">{selectedRecord.action_type}</span>
                  </div>
                </div>
                
                {modalData.session ? (
                  // Interview session details
                  <div className="space-y-4">
                    <div className="bg-gray-750 rounded-lg p-4">
                      <h4 className="font-bold text-white mb-2">Interview Session</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-gray-400">Role:</span>
                          <span className="text-white ml-2">{modalData.session.role}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Experience Level:</span>
                          <span className="text-white ml-2">{modalData.session.experience_level}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Status:</span>
                          <span className="text-white ml-2 capitalize">{modalData.session.status}</span>
                        </div>
                        {modalData.session.final_score && (
                          <div>
                            <span className="text-gray-400">Final Score:</span>
                            <span className="text-white ml-2">{modalData.session.final_score}/100</span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {modalData.questions && modalData.questions.length > 0 && (
                      <div className="bg-gray-750 rounded-lg p-4">
                        <h4 className="font-bold text-white mb-2">Questions & Answers</h4>
                        <div className="space-y-4">
                          {modalData.questions.map((question: any, index: number) => {
                            const answer = modalData.answers?.find((a: any) => a.question_id === question.id);
                            return (
                              <div key={question.id} className="border-l-4 border-purple-500 pl-4 py-2">
                                <div className="text-white font-medium mb-1">
                                  Q{index + 1}: {question.question_text}
                                </div>
                                {answer && (
                                  <div className="text-gray-300 mt-2">
                                    <span className="font-medium">Your Answer:</span>
                                    <p className="mt-1">{answer.answer_text}</p>
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                    
                    {modalData.session.overall_feedback && (
                      <div className="bg-gray-750 rounded-lg p-4">
                        <h4 className="font-bold text-white mb-2">Overall Feedback</h4>
                        <p className="text-gray-300">{modalData.session.overall_feedback}</p>
                      </div>
                    )}
                    
                    {modalData.session.strengths && modalData.session.strengths.length > 0 && (
                      <div className="bg-gray-750 rounded-lg p-4">
                        <h4 className="font-bold text-white mb-2">Strengths</h4>
                        <ul className="list-disc list-inside text-gray-300 space-y-1">
                          {modalData.session.strengths.map((strength: string, index: number) => (
                            <li key={index}>{strength}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {modalData.session.weaknesses && modalData.session.weaknesses.length > 0 && (
                      <div className="bg-gray-750 rounded-lg p-4">
                        <h4 className="font-bold text-white mb-2">Areas for Improvement</h4>
                        <ul className="list-disc list-inside text-gray-300 space-y-1">
                          {modalData.session.weaknesses.map((weakness: string, index: number) => (
                            <li key={index}>{weakness}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  // Other agent details
                  <div className="bg-gray-750 rounded-lg p-4">
                    <h4 className="font-bold text-white mb-2">Full Output</h4>
                    <pre className="text-gray-300 text-sm whitespace-pre-wrap">
                      {modalData.full_output}
                    </pre>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                No details available
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryPage;