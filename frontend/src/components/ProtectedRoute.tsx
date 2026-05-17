import type { ReactNode } from 'react';

import { useAuth } from './AuthProvider';
import { LoginPage } from '../pages/LoginPage';

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <main className="pageShell">
        <p className="mutedText">Loading session...</p>
      </main>
    );
  }

  if (user == null) {
    return <LoginPage />;
  }

  return <>{children}</>;
}
