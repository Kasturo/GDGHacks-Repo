import { useState } from 'react';

export function LandingPage({ onHealthCheck, healthMessage, ActionButton }) {
  const [signedInUser] = useState(() => {
    try {
      const rawUser = localStorage.getItem('current_user');
      return rawUser ? JSON.parse(rawUser) : null;
    } catch {
      return null;
    }
  });

  return (
    <main className="mx-auto grid min-h-svh w-full place-items-center gap-4 p-8 text-center">
      <h1 className="m-0 text-5xl font-medium tracking-tight text-foreground md:text-6xl">Landing</h1>
      {signedInUser?.email && (
        <p className="max-w-2xl text-sm text-emerald-600">
          Signed in as {signedInUser.email}
        </p>
      )}
      <ActionButton onClick={onHealthCheck}>Test API</ActionButton>
      {healthMessage && <p className="max-w-2xl text-sm text-muted-foreground">{healthMessage}</p>}
    </main>
  );
}
