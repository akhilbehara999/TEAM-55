import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

interface AnalysisResult {
  ats_score: number;
  gen_z_roast: string;
  professional_fixes: string[];
  status: string;
}

const ResumeAnalyzerPage = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    if (!file) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8001/api/analyze/resume/file', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setAnalysisResult(data);
    } catch (err) {
      setError('Failed to analyze resume. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setAnalysisResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-blue-500';
    return 'text-red-500';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-blue-500';
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
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">📄 Resume Intelligence</h1>
          <p className="text-gray-300 text-sm sm:text-base max-w-2xl mx-auto">Upload your resume for instant ATS optimization and professional enhancement tips.</p>
        </div>

        {!analysisResult ? (
          <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-6 sm:p-8 backdrop-blur-sm bg-opacity-90">
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Select PDF Resume
              </label>
              <div className="flex items-center">
                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-blue-500 rounded-lg cursor-pointer bg-gray-700 hover:bg-gray-600 transition-colors">
                  <div className="flex flex-col items-center justify-center pt-3 pb-4">
                    <svg className="w-8 h-8 mb-3 text-blue-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                      <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                    </svg>
                    <p className="mb-2 text-sm text-gray-400">
                      <span className="font-semibold">Tap to upload</span>
                    </p>
                    <p className="text-xs text-gray-500 px-2 text-center">PDF files only (max 10MB)</p>
                  </div>
                  <input 
                    type="file" 
                    ref={fileInputRef}
                    className="hidden" 
                    accept=".pdf" 
                    onChange={handleFileChange}
                  />
                </label>
              </div>
              {file && (
                <p className="mt-2 text-sm text-blue-400 truncate">
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
                    : 'bg-gradient-to-r from-blue-600 to-indigo-700 text-white hover:from-blue-700 hover:to-indigo-800 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                }`}
              >
                {isAnalyzing ? 'Analyzing Resume...' : 'Analyze Resume'}
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* ATS Score Card */}
            <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-5 sm:p-6 backdrop-blur-sm bg-opacity-90">
              <h2 className="text-xl sm:text-2xl font-bold text-white mb-4">📊 ATS Compatibility Score</h2>
              <div className="flex flex-col items-center">
                <div className="text-center mb-4">
                  <div className={`text-5xl sm:text-6xl font-bold ${getScoreColor(analysisResult.ats_score)}`}>
                    {analysisResult.ats_score}<span className="text-xl sm:text-2xl">/100</span>
                  </div>
                  <div className="mt-2 w-24 h-2 bg-gray-700 rounded-full overflow-hidden mx-auto">
                    <div 
                      className={`h-full ${getScoreBgColor(analysisResult.ats_score)}`} 
                      style={{ width: `${analysisResult.ats_score}%` }}
                    ></div>
                  </div>
                </div>
                <div className="w-full">
                  <p className="text-gray-300 text-sm sm:text-base text-center">{analysisResult.gen_z_roast}</p>
                </div>
              </div>
            </div>

            {/* Professional Fixes Card */}
            <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-5 sm:p-6 backdrop-blur-sm bg-opacity-90">
              <h2 className="text-xl sm:text-2xl font-bold text-white mb-4 flex items-center">
                <span className="mr-2">💼</span> Professional Fixes
              </h2>
              <ul className="space-y-3">
                {analysisResult.professional_fixes.map((fix: string, index: number) => (
                  <li key={index} className="flex items-start">
                    <div className="flex-shrink-0 mt-1">
                      <div className="w-5 h-5 sm:w-6 sm:h-6 rounded-full bg-blue-500 flex items-center justify-center">
                        <svg className="w-3 h-3 sm:w-4 sm:h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                      </div>
                    </div>
                    <span className="ml-2 sm:ml-3 text-gray-300 text-sm sm:text-base">{fix}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="flex justify-center">
              <button
                onClick={handleReset}
                className="w-full sm:w-auto px-5 py-3 bg-gray-700 text-white rounded-lg font-medium hover:bg-gray-600 transition-colors border border-gray-600"
              >
                Analyze Another Resume
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeAnalyzerPage;