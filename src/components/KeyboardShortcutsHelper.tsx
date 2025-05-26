import React, { useState } from 'react';
import { Card } from './ui/card';

interface ShortcutInfo {
  key: string;
  description: string;
  modifiers?: {
    ctrl?: boolean;
    shift?: boolean;
    alt?: boolean;
  };
}

const SHORTCUTS: ShortcutInfo[] = [
  { key: 'm', description: 'Toggle monitoring dashboard' },
  { key: 't', description: 'Focus trading input', modifiers: { ctrl: true } },
  { key: 'r', description: 'Refresh market data', modifiers: { ctrl: true } },
  { key: '/', description: 'Show keyboard shortcuts' },
  { key: 'Escape', description: 'Close current modal/popup' },
  { key: 's', description: 'Quick save settings', modifiers: { ctrl: true } },
  { key: 'h', description: 'Toggle high contrast mode' },
  { key: '1-5', description: 'Switch between main sections', modifiers: { alt: true } }
];

const KeyboardShortcutsHelper: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);

  const formatShortcut = (shortcut: ShortcutInfo) => {
    const parts = [];
    if (shortcut.modifiers?.ctrl) parts.push('Ctrl');
    if (shortcut.modifiers?.alt) parts.push('Alt');
    if (shortcut.modifiers?.shift) parts.push('Shift');
    parts.push(shortcut.key.toUpperCase());
    return parts.join(' + ');
  };

  return (
    <>
      <button
        onClick={() => setIsVisible(true)}
        className="fixed bottom-4 left-4 p-2 bg-gray-800 text-white rounded-full shadow-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
        title="Show keyboard shortcuts"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
          />
        </svg>
      </button>

      {isVisible && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-lg p-6 bg-white rounded-lg shadow-xl">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Keyboard Shortcuts</h2>
              <button
                onClick={() => setIsVisible(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {SHORTCUTS.map((shortcut, index) => (
                <div
                  key={index}
                  className="flex justify-between items-center p-2 hover:bg-gray-50 rounded"
                >
                  <span className="text-gray-600">{shortcut.description}</span>
                  <kbd className="px-2 py-1 bg-gray-100 border border-gray-300 rounded text-sm">
                    {formatShortcut(shortcut)}
                  </kbd>
                </div>
              ))}
            </div>

            <p className="mt-4 text-sm text-gray-500">
              Press '/' at any time to show this help dialog
            </p>
          </Card>
        </div>
      )}
    </>
  );
};

export default KeyboardShortcutsHelper;