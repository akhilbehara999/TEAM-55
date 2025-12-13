import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface RiskClause {
  clause_name: string;
  risk_level: 'RED' | 'YELLOW' | 'GREEN';
  negotiation_strategy: string;
}

interface KeyTerms {
  salary_base: string;
  start_date: string;
  pto_days: number;
  signing_bonus: string;
}

interface ContractAnalysis {
  overall_score: number;
  summary: string;
  key_terms: KeyTerms;
  risk_clauses: RiskClause[];
}

const ContractGuardianPage = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<ContractAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
        setError(null);
      } else {
        setError('Please select a PDF file.');
        setFile(null);
      }
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select a file to analyze');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8002/api/analyze/contract', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        // Try to get error details from response
        let errorMessage = 'Analysis failed';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (parseError) {
          // If we can't parse JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(`Server error (${response.status}): ${errorMessage}`);
      }

      const data: ContractAnalysis = await response.json();
      setAnalysis(data);
    } catch (err) {
      // Provide more specific error messages based on the type of error
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('Network error: Unable to connect to the server. Please ensure the backend is running.');
      } else if (err instanceof Error) {
        setError(`Contract processing failed: ${err.message}`);
      } else {
        setError('Contract processing failed. Please ensure the document is a readable PDF and try again.');
      }
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'RED': return 'bg-red-100 text-red-800 border-red-200';
      case 'YELLOW': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'GREEN': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

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
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">⚖️ Contract Guardian</h1>
          <p className="text-gray-300 text-sm sm:text-base max-w-2xl mx-auto">Upload your contract for a detailed risk assessment.</p>
        </div>

        {!analysis && !isAnalyzing && (
          <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-6 sm:p-8 backdrop-blur-sm bg-opacity-90">
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Select PDF Contract
              </label>
              <div className="flex items-center">
                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-green-500 rounded-lg cursor-pointer bg-gray-700 hover:bg-gray-600 transition-colors">
                  <div className="flex flex-col items-center justify-center pt-3 pb-4">
                    <svg className="w-8 h-8 mb-3 text-green-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                      <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                    </svg>
                    <p className="mb-2 text-sm text-gray-400">
                      <span className="font-semibold">Tap to upload</span>
                    </p>
                    <p className="text-xs text-gray-500 px-2 text-center">PDF files only (max 10MB)</p>
                  </div>
                  <input 
                    type="file" 
                    className="hidden" 
                    accept=".pdf" 
                    onChange={handleFileChange}
                  />
                </label>
              </div>
              {file && (
                <p className="mt-2 text-sm text-green-400 truncate">
                  Selected: {file.name}
                </p>
              )}
            </div>

            {error && (
              <div className="mb-5 p-3 sm:p-4 bg-red-900 border border-red-700 rounded-lg">
                <p className="text-red-200 text-sm">{error}</p>
              </div>
            )}

            <div className="flex justify-center">
              <button
                onClick={handleAnalyze}
                disabled={!file || isAnalyzing}
                className={`w-full py-3 sm:py-4 rounded-lg font-semibold text-base sm:text-lg transition-all ${
                  !file || isAnalyzing
                    ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-green-600 to-emerald-700 text-white hover:from-green-700 hover:to-emerald-800 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                }`}
              >
                Analyze Contract
              </button>
            </div>
          </div>
        )}

        {isAnalyzing && (
          <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-6 sm:p-8 backdrop-blur-sm bg-opacity-90 text-center">
            <div className="flex flex-col items-center justify-center py-8 sm:py-12">
              <div className="animate-spin rounded-full h-12 w-12 sm:h-16 sm:w-16 border-t-4 border-b-4 border-green-500 mb-4 sm:mb-6"></div>
              <h2 className="text-xl sm:text-2xl font-bold text-white mb-2">Analyzing Contract...</h2>
              <p className="text-gray-300 text-sm sm:text-base">Processing {file?.name || 'your contract'}... This usually takes 10-20 seconds.</p>
            </div>
          </div>
        )}

        {analysis && (
          <div className="space-y-6">
            {/* Summary Card */}
            <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-5 sm:p-6 backdrop-blur-sm bg-opacity-90">
              <h2 className="text-xl sm:text-2xl font-bold text-white mb-4">⚖️ Safety Score</h2>
              <div className="flex flex-col items-center">
                <div className="text-center mb-4">
                  <div className={`text-5xl sm:text-6xl font-bold ${getScoreColor(analysis.overall_score)}`}>
                    {analysis.overall_score}<span className="text-xl sm:text-2xl">/100</span>
                  </div>
                  <div className="mt-2 w-24 h-2 bg-gray-700 rounded-full overflow-hidden mx-auto">
                    <div 
                      className={`h-full ${getScoreBgColor(analysis.overall_score)}`} 
                      style={{ width: `${analysis.overall_score}%` }}
                    ></div>
                  </div>
                  <div className={`mt-3 px-3 py-1 sm:px-4 sm:py-2 rounded-full inline-block font-semibold text-xs sm:text-sm ${
                    analysis.overall_score >= 80 
                      ? 'bg-green-900 text-green-300 border border-green-700' 
                      : analysis.overall_score >= 60 
                        ? 'bg-yellow-900 text-yellow-300 border border-yellow-700' 
                        : 'bg-red-900 text-red-300 border border-red-700'
                  }`}>
                    {analysis.overall_score >= 80 ? 'LOW RISK' : analysis.overall_score >= 60 ? 'MODERATE RISK' : 'HIGH RISK'}
                  </div>
                </div>
                <div className="w-full">
                  <p className="text-gray-300 text-sm sm:text-base text-center">{analysis.summary}</p>
                </div>
              </div>
            </div>

            {/* Risk Clauses Card */}
            <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-5 sm:p-6 backdrop-blur-sm bg-opacity-90">
              <h2 className="text-xl sm:text-2xl font-bold text-white mb-4">🚩 Key Risk Clauses</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700">
                  <thead>
                    <tr>
                      <th className="px-3 py-2 sm:px-4 sm:py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Clause</th>
                      <th className="px-3 py-2 sm:px-4 sm:py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Risk</th>
                      <th className="px-3 py-2 sm:px-4 sm:py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Strategy</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {analysis.risk_clauses.map((clause, index) => (
                      <tr key={index}>
                        <td className="px-3 py-2 sm:px-4 sm:py-3 whitespace-nowrap text-xs sm:text-sm text-white">{clause.clause_name}</td>
                        <td className="px-3 py-2 sm:px-4 sm:py-3 whitespace-nowrap">
                          <span className={`px-2 py-1 sm:px-3 sm:py-1 inline-flex text-xs leading-4 font-semibold rounded-full border ${getRiskColor(clause.risk_level)}`}>
                            {clause.risk_level}
                          </span>
                        </td>
                        <td className="px-3 py-2 sm:px-4 sm:py-3 text-xs sm:text-sm text-gray-300">{clause.negotiation_strategy}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Key Terms Card */}
            <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-5 sm:p-6 backdrop-blur-sm bg-opacity-90">
              <h2 className="text-xl sm:text-2xl font-bold text-white mb-4">🔑 Key Terms</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div className="bg-gray-700 rounded-lg p-3 sm:p-4 border border-gray-600">
                  <h3 className="text-gray-400 text-xs sm:text-sm font-medium mb-1">Base Salary</h3>
                  <p className="text-white text-sm sm:text-base">{analysis.key_terms.salary_base}</p>
                </div>
                <div className="bg-gray-700 rounded-lg p-3 sm:p-4 border border-gray-600">
                  <h3 className="text-gray-400 text-xs sm:text-sm font-medium mb-1">Start Date</h3>
                  <p className="text-white text-sm sm:text-base">{analysis.key_terms.start_date}</p>
                </div>
                <div className="bg-gray-700 rounded-lg p-3 sm:p-4 border border-gray-600">
                  <h3 className="text-gray-400 text-xs sm:text-sm font-medium mb-1">PTO Days</h3>
                  <p className="text-white text-sm sm:text-base">{analysis.key_terms.pto_days}</p>
                </div>
                <div className="bg-gray-700 rounded-lg p-3 sm:p-4 border border-gray-600">
                  <h3 className="text-gray-400 text-xs sm:text-sm font-medium mb-1">Signing Bonus</h3>
                  <p className="text-white text-sm sm:text-base">{analysis.key_terms.signing_bonus}</p>
                </div>
              </div>
            </div>

            <div className="flex justify-center">
              <button
                onClick={() => {
                  setAnalysis(null);
                  setFile(null);
                }}
                className="w-full sm:w-auto px-5 py-3 bg-gray-700 text-white rounded-lg font-medium hover:bg-gray-600 transition-colors border border-gray-600"
              >
                Analyze Another Contract
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContractGuardianPage;