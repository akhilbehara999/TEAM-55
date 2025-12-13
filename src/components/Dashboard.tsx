import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('dashboard');

  const handleLogout = () => {
    // In a real app, you would clear the auth token here
    navigate('/');
  };

  const handleAgentAction = (agent: string) => {
    if (agent === 'resume') {
      navigate('/resume-analyzer');
    } else if (agent === 'interview') {
      navigate('/interview-simulator');
    } else if (agent === 'contract') {
      navigate('/contract-guardian');
    } else if (agent === 'docs') {
      navigate('/auto-docs');
    } else {
      console.log(`Activating ${agent}`);
      // Implement other agent activation logic here
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-900 flex flex-col">
      {/* Header with Navigation Menu and Logout Button */}
      <header className="py-4 px-4 sm:px-6 bg-gray-800 border-b border-gray-700 flex items-center justify-between">
        {/* Persistent 3-line Vertical Menu */}
        <div className="flex flex-col space-y-1">
          {[
            { id: 'dashboard', label: 'Dashboard' },
            { id: 'history', label: 'History' },
            { id: 'settings', label: 'Settings' }
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveNav(item.id)}
              className={`px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                activeNav === item.id
                  ? 'bg-teal-900 text-teal-400 border border-teal-700'
                  : 'text-gray-400 hover:bg-gray-700'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>

        {/* Logo/Title */}
        <div className="flex-1 flex justify-center">
          <div className="flex items-center">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center">
              <span className="text-white font-bold text-sm">CF</span>
            </div>
            <h1 className="ml-2 text-lg sm:text-xl font-bold text-white">CareerFlow AI</h1>
          </div>
        </div>

        {/* Modern Logout Button */}
        <button
          onClick={handleLogout}
          className="flex items-center px-3 py-2 rounded-lg bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5 border border-red-500"
          aria-label="Logout"
        >
          <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
          </svg>
          <span className="ml-2 text-xs sm:text-sm font-medium hidden sm:inline">Logout</span>
        </button>
      </header>

      {/* Main Content */}
      <main className="flex-1 py-4 sm:py-8 px-4 sm:px-6 bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-6 sm:mb-8">
            <h2 className="text-xl sm:text-2xl font-bold text-white mb-1">Your Agent Hub</h2>
            <p className="text-gray-400 text-sm">Select a co-pilot to continue your journey</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
            {/* Resume Intelligence Agent */}
            <div className="bg-gray-800 rounded-xl sm:rounded-2xl border border-gray-700 p-4 sm:p-6 shadow-lg hover:shadow-xl transition-all hover:border-blue-500">
              <div className="border-t-4 border-blue-500 rounded-t-xl sm:rounded-t-2xl -mt-4 -mx-4 sm:-mt-6 sm:-mx-6 mb-4 sm:mb-5 pt-3 sm:pt-4 px-3 sm:px-5">
                <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-lg sm:rounded-xl bg-blue-900 flex items-center justify-center mb-3 sm:mb-4">
                  <span className="text-xl sm:text-2xl">📄</span>
                </div>
                <h2 className="text-lg sm:text-xl font-bold text-white mb-2">Resume Intelligence</h2>
                <p className="text-gray-400 text-xs sm:text-sm mb-4">
                  Upload your resume and get immediate ATS optimization and professional fixes.
                </p>
                <button
                  onClick={() => handleAgentAction('resume')}
                  className="w-full py-2 sm:py-3 bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white rounded-lg font-medium transition-all transform hover:-translate-y-0.5 text-sm sm:text-base"
                >
                  Activate Agent
                </button>
              </div>
            </div>

            {/* Interview Simulation Agent */}
            <div className="bg-gray-800 rounded-xl sm:rounded-2xl border border-gray-700 p-4 sm:p-6 shadow-lg hover:shadow-xl transition-all hover:border-purple-500">
              <div className="border-t-4 border-purple-500 rounded-t-xl sm:rounded-t-2xl -mt-4 -mx-4 sm:-mt-6 sm:-mx-6 mb-4 sm:mb-5 pt-3 sm:pt-4 px-3 sm:px-5">
                <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-lg sm:rounded-xl bg-purple-900 flex items-center justify-center mb-3 sm:mb-4">
                  <span className="text-xl sm:text-2xl">🎤</span>
                </div>
                <h2 className="text-lg sm:text-xl font-bold text-white mb-2">Interview Simulation</h2>
                <p className="text-gray-400 text-xs sm:text-sm mb-4">
                  Start a context-aware interview based on your resume and target industry.
                </p>
                <button
                  onClick={() => handleAgentAction('interview')}
                  className="w-full py-2 sm:py-3 bg-gradient-to-r from-purple-600 to-indigo-700 hover:from-purple-700 hover:to-indigo-800 text-white rounded-lg font-medium transition-all transform hover:-translate-y-0.5 text-sm sm:text-base"
                >
                  Start Simulation
                </button>
              </div>
            </div>

            {/* Contract Guardian Agent */}
            <div className="bg-gray-800 rounded-xl sm:rounded-2xl border border-gray-700 p-4 sm:p-6 shadow-lg hover:shadow-xl transition-all hover:border-green-500">
              <div className="border-t-4 border-green-500 rounded-t-xl sm:rounded-t-2xl -mt-4 -mx-4 sm:-mt-6 sm:-mx-6 mb-4 sm:mb-5 pt-3 sm:pt-4 px-3 sm:px-5">
                <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-lg sm:rounded-xl bg-green-900 flex items-center justify-center mb-3 sm:mb-4">
                  <span className="text-xl sm:text-2xl">⚖️</span>
                </div>
                <h2 className="text-lg sm:text-xl font-bold text-white mb-2">Contract Guardian</h2>
                <p className="text-gray-400 text-xs sm:text-sm mb-4">
                  Upload offer letters for risk analysis and negotiation insights.
                </p>
                <button
                  onClick={() => handleAgentAction('contract')}
                  className="w-full py-2 sm:py-3 bg-gradient-to-r from-green-600 to-emerald-700 hover:from-green-700 hover:to-emerald-800 text-white rounded-lg font-medium transition-all transform hover:-translate-y-0.5 text-sm sm:text-base"
                >
                  Review Contract
                </button>
              </div>
            </div>

            {/* Auto-Docs Agent */}
            <div className="bg-gray-800 rounded-xl sm:rounded-2xl border border-gray-700 p-4 sm:p-6 shadow-lg hover:shadow-xl transition-all hover:border-orange-500">
              <div className="border-t-4 border-orange-500 rounded-t-xl sm:rounded-t-2xl -mt-4 -mx-4 sm:-mt-6 sm:-mx-6 mb-4 sm:mb-5 pt-3 sm:pt-4 px-3 sm:px-5">
                <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-lg sm:rounded-xl bg-orange-900 flex items-center justify-center mb-3 sm:mb-4">
                  <span className="text-xl sm:text-2xl">💻</span>
                </div>
                <h2 className="text-lg sm:text-xl font-bold text-white mb-2">Auto-Docs</h2>
                <p className="text-gray-400 text-xs sm:text-sm mb-4">
                  Generate professional READMEs and documentation from source code.
                </p>
                <button
                  onClick={() => handleAgentAction('docs')}
                  className="w-full py-2 sm:py-3 bg-gradient-to-r from-orange-600 to-amber-700 hover:from-orange-700 hover:to-amber-800 text-white rounded-lg font-medium transition-all transform hover:-translate-y-0.5 text-sm sm:text-base"
                >
                  Generate Docs
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer Status */}
      <footer className="py-3 sm:py-4 px-4 sm:px-6 bg-gray-800 border-t border-gray-700">
        <div className="max-w-6xl mx-auto flex flex-wrap justify-center gap-3 sm:gap-6 text-xs sm:text-sm text-gray-500">
          <span>ATS Score: 85%</span>
          <span>Interviews: 3</span>
          <span>Active: 5 min ago</span>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;