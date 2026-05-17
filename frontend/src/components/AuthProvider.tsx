import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import {
  clearAuthTokens,
  getCurrentUser,
  getStoredRefreshToken,
  loginUser,
  logoutUser,
  refreshUser,
  registerUser,
  setAuthTokens,
  type ProjectAccess,
  type UserInfo,
} from '../api/client';

type AuthContextValue = {
  user: UserInfo | null;
  activeProject: ProjectAccess | null;
  isLoading: boolean;
  error: string;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
  reloadUser: () => Promise<void>;
  setActiveProjectId: (projectId: number) => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [activeProjectId, setActiveProjectIdState] = useState<number | null>(() => {
    const storedValue = localStorage.getItem('tgi_active_project_id');
    return storedValue == null ? null : Number(storedValue);
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const activeProject = useMemo(() => {
    if (user == null || user.projects.length === 0) {
      return null;
    }
    const selectedProject = user.projects.find((project) => project.project_id === activeProjectId);
    return selectedProject ?? user.projects[0];
  }, [activeProjectId, user]);

  const reloadUser = useCallback(async () => {
    setError('');
    const userData = await getCurrentUser();
    setUser(userData);
    if (userData.projects.length > 0 && activeProjectId == null) {
      setActiveProjectIdState(userData.projects[0].project_id);
      localStorage.setItem('tgi_active_project_id', String(userData.projects[0].project_id));
    }
  }, [activeProjectId]);

  useEffect(() => {
    const bootstrapAuth = async () => {
      setIsLoading(true);
      try {
        if (getStoredRefreshToken() !== '') {
          const authData = await refreshUser();
          setAuthTokens(authData.access_token, authData.refresh_token);
          setUser(authData.user);
          if (authData.user.projects.length > 0 && activeProjectId == null) {
            setActiveProjectIdState(authData.user.projects[0].project_id);
            localStorage.setItem('tgi_active_project_id', String(authData.user.projects[0].project_id));
          }
        }
      } catch {
        clearAuthTokens();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    void bootstrapAuth();
  }, [activeProjectId]);

  const login = async (email: string, password: string) => {
    setError('');
    const authData = await loginUser(email, password);
    setAuthTokens(authData.access_token, authData.refresh_token);
    setUser(authData.user);
    if (authData.user.projects.length > 0) {
      setActiveProjectIdState(authData.user.projects[0].project_id);
      localStorage.setItem('tgi_active_project_id', String(authData.user.projects[0].project_id));
    }
  };

  const register = async (email: string, password: string, fullName: string) => {
    setError('');
    const authData = await registerUser(email, password, fullName);
    setAuthTokens(authData.access_token, authData.refresh_token);
    setUser(authData.user);
  };

  const logout = async () => {
    await logoutUser();
    clearAuthTokens();
    setUser(null);
    setActiveProjectIdState(null);
    localStorage.removeItem('tgi_active_project_id');
  };

  const setActiveProjectId = (projectId: number) => {
    setActiveProjectIdState(projectId);
    localStorage.setItem('tgi_active_project_id', String(projectId));
  };

  const value = {
    user,
    activeProject,
    isLoading,
    error,
    login,
    register,
    logout,
    reloadUser,
    setActiveProjectId,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context == null) {
    throw new Error('Auth context is not available.');
  }
  return context;
}
