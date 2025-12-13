import React from 'react';
import AppRouter from './components/Router';
import { AuthProvider } from './supabase/AuthContext';
import './styles/index.css';

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </div>
  );
}

export default App;