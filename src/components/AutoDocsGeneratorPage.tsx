import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AutoDocsGeneratorPage = () => {
  const navigate = useNavigate();
  const [githubUrl, setGithubUrl] = useState('');
  const [projectTitle, setProjectTitle] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [readmeContent, setReadmeContent] = useState('');
  const [error, setError] = useState<string | null>(null);

  const validateGithubUrl = (url: string) => {
    const githubRegex = /^https:\/\/github\.com\/[\w\-]+\/[\w\-]+(?:\.git)?$/;
    return githubRegex.test(url);
  };

  const handleGenerate = async () => {
    if (!githubUrl) {
      setError('Please enter a GitHub repository URL');
      return;
    }

    if (!validateGithubUrl(githubUrl)) {
      setError('Please enter a valid GitHub repository URL');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setReadmeContent('');

    try {
      const response = await fetch('http://localhost:8000/api/autodocs/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          github_url: githubUrl,
          project_title: projectTitle || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate README');
      }

      const data = await response.json();
      setReadmeContent(data.readme_content);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      console.error('Generation error:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!readmeContent) return;

    const blob = new Blob([readmeContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'README.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 py-6 px-4 sm:px-6">
      {/* Back Button */}
      <div className="max-w-7xl mx-auto mb-4">
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

      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-6">
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">💻 Auto-Docs Generator</h1>
          <p className="text-gray-300 text-sm sm:text-base max-w-2xl mx-auto">Generate professional README.md files for your GitHub repositories</p>
        </div>

        <div className="space-y-6 sm:space-y-0 sm:grid sm:grid-cols-1 gap-6">
          {/* Input Form */}
          <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-6 sm:p-8 backdrop-blur-sm bg-opacity-90">
            <h2 className="text-xl sm:text-2xl font-bold text-white mb-5">Repository Information</h2>
            
            <div className="space-y-5">
              <div>
                <label htmlFor="githubUrl" className="block text-sm font-medium text-gray-300 mb-2">
                  GitHub Repository URL *
                </label>
                <input
                  type="text"
                  id="githubUrl"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  placeholder="https://github.com/user/repo"
                  className="w-full px-4 py-3 bg-gray-700 border border-orange-500 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 text-white placeholder-gray-400"
                />
                <p className="mt-2 text-xs sm:text-sm text-gray-500">
                  Must be a public repository URL
                </p>
              </div>
              
              <div>
                <label htmlFor="projectTitle" className="block text-sm font-medium text-gray-300 mb-2">
                  Project Title (Optional)
                </label>
                <input
                  type="text"
                  id="projectTitle"
                  value={projectTitle}
                  onChange={(e) => setProjectTitle(e.target.value)}
                  placeholder="Leave blank to use repository name"
                  className="w-full px-4 py-3 bg-gray-700 border border-orange-500 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 text-white placeholder-gray-400"
                />
              </div>
              
              {error && (
                <div className="p-3 sm:p-4 bg-red-900 border border-red-700 rounded-lg">
                  <p className="text-red-200 text-sm">{error}</p>
                </div>
              )}
              
              <div className="flex justify-center">
                <button
                  onClick={handleGenerate}
                  disabled={!githubUrl || isGenerating || !validateGithubUrl(githubUrl)}
                  className={`w-full py-3 sm:py-4 rounded-lg font-semibold text-base sm:text-lg transition-all ${
                    !githubUrl || isGenerating || !validateGithubUrl(githubUrl)
                      ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-orange-600 to-amber-700 text-white hover:from-orange-700 hover:to-amber-800 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                  }`}
                >
                  {isGenerating ? 'Generating README...' : 'Generate README'}
                </button>
              </div>
            </div>
          </div>

          {/* Output Viewer */}
          <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-6 sm:p-8 backdrop-blur-sm bg-opacity-90">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-5">
              <h2 className="text-xl sm:text-2xl font-bold text-white mb-3 sm:mb-0">README.md Preview</h2>
              {readmeContent && (
                <button
                  onClick={handleDownload}
                  className="w-full sm:w-auto px-4 py-2 sm:px-5 sm:py-2.5 bg-gradient-to-r from-orange-600 to-amber-700 text-white rounded-lg font-medium hover:from-orange-700 hover:to-amber-800 transition-all flex items-center justify-center"
                >
                  <svg className="w-4 h-4 sm:w-5 sm:h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                  </svg>
                  <span className="text-sm sm:text-base">Download</span>
                </button>
              )}
            </div>

            {isGenerating ? (
              <div className="flex flex-col items-center justify-center py-8 sm:py-12">
                <div className="animate-spin rounded-full h-12 w-12 sm:h-16 sm:w-16 border-t-4 border-b-4 border-orange-500 mb-4 sm:mb-6"></div>
                <h3 className="text-lg sm:text-xl font-bold text-white mb-2">Analyzing Repository...</h3>
                <p className="text-gray-300 text-sm sm:text-base">Cloning repo and analyzing code structure... This may take a moment.</p>
              </div>
            ) : readmeContent ? (
              <div className="bg-gray-900 rounded-lg border border-gray-700 p-3 sm:p-4 h-96 overflow-auto">
                <pre className="text-gray-300 text-xs sm:text-sm whitespace-pre-wrap font-mono">
                  {readmeContent}
                </pre>
              </div>
            ) : (
              <div className="flex items-center justify-center h-96 border-2 border-dashed border-gray-700 rounded-lg">
                <div className="text-center p-6">
                  <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-full bg-gray-700 flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 sm:w-8 sm:h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                  </div>
                  <h3 className="text-base sm:text-lg font-medium text-gray-400 mb-1">Generated README will appear here</h3>
                  <p className="text-gray-500 text-xs sm:text-sm">Enter a GitHub repository URL and click "Generate README"</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutoDocsGeneratorPage;