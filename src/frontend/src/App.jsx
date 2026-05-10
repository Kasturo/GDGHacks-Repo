import { useState } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { Button } from './components/ui/button';
import { DmsPage } from './pages/DmsPage';
import { LandingPage } from './pages/LandingPage';
import { ProfilePage } from './pages/ProfilePage';
import { SignInPage } from './pages/SignInPage';
import { SignUpPage } from './pages/SignUpPage';

function App() {
  const [result, setResult] = useState('');

  const callApi = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/health`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      setResult(`API status: ${data.status}`);
    } catch (error) {
      setResult(
        `API request failed. Confirm backend is running and CORS allows your frontend origin. (${error.message})`,
      );
    }
  };

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/landing" replace />} />
      <Route
        path="/landing"
        element={<LandingPage onHealthCheck={callApi} healthMessage={result} ActionButton={Button} />}
      />
      <Route path="/signin" element={<SignInPage/>} />
      <Route path="/signup" element={<SignUpPage/>} />
      <Route path="/profile" element={<ProfilePage />} />
      <Route path="/dms" element={<DmsPage />} />
    </Routes>
  );
}
export default App;