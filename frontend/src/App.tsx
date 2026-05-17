import { AuthProvider } from './components/AuthProvider';
import { ProtectedRoute } from './components/ProtectedRoute';
import { HomePage } from './pages/HomePage';

import './styles.css';

export function App() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <HomePage />
      </ProtectedRoute>
    </AuthProvider>
  );
}
