import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './LandingPage';
import AuthPage from './AuthPage';
import Dashboard from './Dashboard';
import ResumeAnalyzerPage from './ResumeAnalyzerPage';
import InterviewSimulatorPage from './InterviewSimulatorPage';
import ContractGuardianPage from './ContractGuardianPage';
import AutoDocsGeneratorPage from './AutoDocsGeneratorPage';
import HistoryPage from './HistoryPage';
import SettingsPage from './SettingsPage';

const AppRouter = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<AuthPage />} />
        <Route path="/signup" element={<AuthPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/resume-analyzer" element={<ResumeAnalyzerPage />} />
        <Route path="/interview-simulator" element={<InterviewSimulatorPage />} />
        <Route path="/contract-guardian" element={<ContractGuardianPage />} />
        <Route path="/auto-docs" element={<AutoDocsGeneratorPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </Router>
  );
};

export default AppRouter;