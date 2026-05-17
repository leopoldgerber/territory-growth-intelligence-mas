import { useState } from 'react';

import { useAuth } from '../components/AuthProvider';

export function LoginPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const submitForm = async () => {
    setIsLoading(true);
    setError('');
    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await register(email, password, fullName);
      }
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Authentication failed';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="authShell">
      <section className="authPanel">
        <p className="eyebrow">Territory Growth Intelligence MAS</p>
        <h1>{mode === 'login' ? 'Sign in' : 'Create account'}</h1>
        <div className="authForm">
          {mode === 'register' && (
            <label>
              Full name
              <input value={fullName} onChange={(event) => setFullName(event.target.value)} />
            </label>
          )}
          <label>
            Email
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" />
          </label>
          <label>
            Password
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" />
          </label>
          <button type="button" onClick={submitForm} disabled={isLoading}>
            {isLoading ? 'Please wait...' : mode === 'login' ? 'Login' : 'Register'}
          </button>
          <button className="secondaryButton" type="button" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
            {mode === 'login' ? 'Create first account' : 'Back to login'}
          </button>
        </div>
        {error && <p className="errorText">{error}</p>}
      </section>
    </main>
  );
}
