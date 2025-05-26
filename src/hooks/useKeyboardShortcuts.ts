import { useEffect, useCallback } from 'react';
import { useNotification } from './useNotification';

type KeyCommand = {
  key: string;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  description: string;
  action: () => void;
};

export function useKeyboardShortcuts(commands: KeyCommand[]) {
  const { addNotification } = useNotification();

  const handleKeyPress = useCallback((event: KeyboardEvent) => {
    // Ignore if user is typing in an input or textarea
    if (
      event.target instanceof HTMLInputElement ||
      event.target instanceof HTMLTextAreaElement
    ) {
      return;
    }

    const matchingCommand = commands.find(cmd => (
      cmd.key.toLowerCase() === event.key.toLowerCase() &&
      !!cmd.ctrlKey === event.ctrlKey &&
      !!cmd.shiftKey === event.shiftKey &&
      !!cmd.altKey === event.altKey
    ));

    if (matchingCommand) {
      event.preventDefault();
      matchingCommand.action();
      addNotification('info', `Executed: ${matchingCommand.description}`, 2000);
    }
  }, [commands, addNotification]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handleKeyPress]);
}