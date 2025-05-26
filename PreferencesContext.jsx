import { createContext, useContext, useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface Preferences {
  [key: string]: any;
}

interface PreferencesContextType {
  preferences: Preferences | null;
  error: string | null;
  loading: boolean;
  updatePreference: (params: UpdatePreferenceParams) => Promise<void>;
}

interface UpdatePreferenceParams {
  category: string;
  key: string;
  value: any;
}

const PreferencesContext = createContext<PreferencesContextType | null>(null);

export const PreferencesProvider = ({ children }) => {
  const [preferences, setPreferences] = useState<Preferences | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.hostname}:8765/ws/preferences`;
  const MAX_RETRIES = 3;
  const RETRY_DELAY = 2000;

  const { isConnected, send } = useWebSocket(WS_URL, {
    onMessage: (message) => {
      if (message.type === 'preferences_update') {
        setPreferences(message.data);
        setLoading(false);
        setError(null);
      }
    },
    onError: (err) => {
      console.error('WebSocket error:', err);
      setError('Failed to connect to preferences service');
      setLoading(false);
    },
    reconnectOptions: {
      maxRetries: MAX_RETRIES,
      delay: RETRY_DELAY,
    }
  });

  const updatePreference = async ({ category, key, value }: UpdatePreferenceParams) => {
    try {
      if (!isConnected) {
        throw new Error('WebSocket connection not available');
      }

      send({
        type: 'update_preference',
        data: { category, key, value }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update preference');
      throw err;
    }
  };

  const contextValue: PreferencesContextType = {
    preferences,
    error,
    loading,
    updatePreference
  };

  return (
    <PreferencesContext.Provider value={contextValue}>
      {children}
    </PreferencesContext.Provider>
  );
};

export const usePreferences = () => {
  const context = useContext(PreferencesContext);
  if (!context) {
    throw new Error('usePreferences must be used within a PreferencesProvider');
  }
  return context;
};