import { useState, useEffect, useCallback } from 'react';
import { preferencesManager, UserPrefs } from '../services/preferencesManager';
import { useWeb3 } from '../contexts/Web3Context';

export function usePreferences() {
  const [preferences, setPreferences] = useState<UserPrefs | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { account } = useWeb3();

  useEffect(() => {
    if (!account) return;

    const loadPreferences = async () => {
      try {
        const prefs = await preferencesManager.getUserPreferences(account);
        setPreferences(prefs);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to load preferences'));
      } finally {
        setIsLoading(false);
      }
    };

    loadPreferences();
  }, [account]);

  const updatePreferences = useCallback(async (updates: Partial<UserPrefs>) => {
    if (!account || !preferences) return;

    try {
      const updated = await preferencesManager.updatePreferences(account, updates);
      setPreferences(updated);
      setError(null);
      return updated;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to update preferences'));
      throw err;
    }
  }, [account, preferences]);

  const exportPreferences = useCallback(async () => {
    if (!account) throw new Error('No wallet connected');
    return preferencesManager.exportPreferences(account);
  }, [account]);

  const importPreferences = useCallback(async (data: string) => {
    if (!account) throw new Error('No wallet connected');
    const success = await preferencesManager.importPreferences(account, data);
    if (success) {
      const prefs = await preferencesManager.getUserPreferences(account);
      setPreferences(prefs);
    }
    return success;
  }, [account]);

  return {
    preferences,
    isLoading,
    error,
    updatePreferences,
    exportPreferences,
    importPreferences
  };
}