import { useState } from 'react';
import { Button } from './components/ui/button';

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
    <main className="mx-auto grid min-h-svh w-full place-items-center gap-4 p-8 text-center">
      <h1 className="m-0 text-5xl font-medium tracking-tight text-foreground md:text-6xl">EC2-Ready App</h1>
      <Button onClick={callApi}>Test API</Button>
      {result && <p className="max-w-2xl text-sm text-muted-foreground">{result}</p>}
    </main>
  );
}
export default App;