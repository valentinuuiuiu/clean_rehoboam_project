import React, { useState, useEffect } from 'react';
import { useNotification } from './contexts/NotificationContext';
import { useAsyncHandler } from './hooks/useAsyncHandler';
import { Card } from './components/ui/card';
import { Progress } from './components/ui/progress';
import { ErrorMessage } from './components/ErrorMessage';

const UserSettings: React.FC = () => {
  const { addNotification } = useNotification();
  const { handleAsync, error } = useAsyncHandler({
    loadingKey: 'user-settings',
    successMessage: 'Settings saved successfully',
    errorMessage: 'Failed to save settings'
  });

  const [settings, setSettings] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    handleAsync(async () => {
      // Fetch user settings
      const response = await fetch('/api/user-settings');
      const data = await response.json();
      setSettings(data);
    }).finally(() => setIsLoading(false));
  }, [handleAsync]);

  const saveSettings = async () => {
    handleAsync(async () => {
      // Save user settings
      const response = await fetch('/api/user-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });
      const result = await response.json();
      addNotification('success', `Settings saved: ${result.message}`);
    });
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500" />
          <span>Loading user settings...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return <ErrorMessage error={error} />;
  }

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">User Settings</h2>
      {settings ? (
        <div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">Username</label>
            <input
              type="text"
              value={settings.username}
              onChange={(e) => setSettings({ ...settings, username: e.target.value })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              value={settings.email}
              onChange={(e) => setSettings({ ...settings, email: e.target.value })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          <button
            onClick={saveSettings}
            className={`px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={isLoading}
          >
            {isLoading ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      ) : (
        <p className="text-gray-500">No user settings available.</p>
      )}
    </Card>
  );
};

export default UserSettings;