"""User settings and preferences manager for trading platform."""
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class UserPreferences:
    """Manage user preferences and trading profile settings."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.preferences_dir = Path("data/user_preferences")
        self.preferences_file = self.preferences_dir / f"{user_id}_preferences.json"
        self.default_preferences = {
            'trading': {
                'max_position_size': 0.1,
                'risk_tolerance': 'medium',
                'preferred_chains': ['ethereum', 'polygon'],
                'auto_trade': False,
                'notification_channels': ['email', 'websocket']
            },
            'ui': {
                'theme': 'light',
                'chart_interval': '1h',
                'default_view': 'portfolio',
                'notifications_enabled': True,
                'sound_enabled': True
            },
            'analysis': {
                'preferred_timeframes': ['1h', '4h', '1d'],
                'indicators': ['RSI', 'MACD', 'BB'],
                'emotion_alerts': True,
                'risk_alerts': True
            },
            'rehoboam': {
                'ai_model': 'anthropic/claude-2',
                'analysis_frequency': 300,  # seconds
                'confidence_threshold': 0.7,
                'max_concurrent_positions': 5
            }
        }
        self._ensure_directory()
        self._load_preferences()

    def _ensure_directory(self):
        """Ensure preferences directory exists."""
        self.preferences_dir.mkdir(parents=True, exist_ok=True)

    def _load_preferences(self):
        """Load user preferences from file."""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r') as f:
                    self.preferences = json.load(f)
            else:
                self.preferences = self.default_preferences.copy()
                self._save_preferences()
        except Exception as e:
            logger.error(f"Error loading preferences: {str(e)}")
            self.preferences = self.default_preferences.copy()

    def _save_preferences(self):
        """Save preferences to file."""
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving preferences: {str(e)}")

    def get_preference(self, category: str, key: str) -> Any:
        """Get specific preference value."""
        try:
            return self.preferences[category][key]
        except KeyError:
            return self.default_preferences.get(category, {}).get(key)

    def set_preference(self, category: str, key: str, value: Any):
        """Set specific preference value."""
        if category not in self.preferences:
            self.preferences[category] = {}
        self.preferences[category][key] = value
        self._save_preferences()

    def update_preferences(self, updates: Dict[str, Dict[str, Any]]):
        """Bulk update preferences."""
        for category, values in updates.items():
            if category not in self.preferences:
                self.preferences[category] = {}
            self.preferences[category].update(values)
        self._save_preferences()

    def reset_category(self, category: str):
        """Reset category to default values."""
        if category in self.default_preferences:
            self.preferences[category] = self.default_preferences[category].copy()
            self._save_preferences()

    def reset_all(self):
        """Reset all preferences to default values."""
        self.preferences = self.default_preferences.copy()
        self._save_preferences()

    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all user preferences."""
        return self.preferences.copy()

    def export_preferences(self, export_path: Optional[str] = None) -> str:
        """Export preferences to JSON file."""
        if not export_path:
            export_path = self.preferences_dir / f"{self.user_id}_preferences_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(export_path, 'w') as f:
                json.dump({
                    'user_id': self.user_id,
                    'timestamp': datetime.now().isoformat(),
                    'preferences': self.preferences
                }, f, indent=2)
            return str(export_path)
        except Exception as e:
            logger.error(f"Error exporting preferences: {str(e)}")
            return ""

    def import_preferences(self, import_path: str) -> bool:
        """Import preferences from JSON file."""
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)
                if 'preferences' in data:
                    self.preferences = data['preferences']
                    self._save_preferences()
                    return True
        except Exception as e:
            logger.error(f"Error importing preferences: {str(e)}")
        return False

    def validate_preferences(self) -> Dict[str, Any]:
        """Validate current preferences and return any issues."""
        issues = []
        
        # Validate trading preferences
        trading = self.preferences.get('trading', {})
        if not 0 <= trading.get('max_position_size', 0) <= 1:
            issues.append("Invalid max_position_size. Must be between 0 and 1.")
        
        # Validate UI preferences
        ui = self.preferences.get('ui', {})
        valid_themes = ['light', 'dark', 'system']
        if ui.get('theme') not in valid_themes:
            issues.append(f"Invalid theme. Must be one of: {valid_themes}")
        
        # Validate analysis preferences
        analysis = self.preferences.get('analysis', {})
        valid_timeframes = ['1m', '5m', '15m', '1h', '4h', '1d', '1w']
        invalid_timeframes = [t for t in analysis.get('preferred_timeframes', [])
                            if t not in valid_timeframes]
        if invalid_timeframes:
            issues.append(f"Invalid timeframes: {invalid_timeframes}")
        
        # Validate Rehoboam preferences
        rehoboam = self.preferences.get('rehoboam', {})
        if not 0 <= rehoboam.get('confidence_threshold', 0) <= 1:
            issues.append("Invalid confidence_threshold. Must be between 0 and 1.")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

class UserPreferencesManager:
    """Manage preferences for all users."""
    
    def __init__(self):
        self.users: Dict[str, UserPreferences] = {}
        self.preferences_dir = Path("data/user_preferences")
        self._load_all_users()

    def _load_all_users(self):
        """Load preferences for all existing users."""
        if not self.preferences_dir.exists():
            return
            
        for pref_file in self.preferences_dir.glob("*_preferences.json"):
            user_id = pref_file.stem.replace("_preferences", "")
            self.users[user_id] = UserPreferences(user_id)

    def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get or create user preferences."""
        if user_id not in self.users:
            self.users[user_id] = UserPreferences(user_id)
        return self.users[user_id]

    def delete_user_preferences(self, user_id: str) -> bool:
        """Delete user preferences."""
        try:
            if user_id in self.users:
                pref_file = self.preferences_dir / f"{user_id}_preferences.json"
                if pref_file.exists():
                    pref_file.unlink()
                del self.users[user_id]
                return True
        except Exception as e:
            logger.error(f"Error deleting preferences for user {user_id}: {str(e)}")
        return False

    def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """Get preferences summary for all users."""
        return {
            user_id: prefs.get_all_preferences()
            for user_id, prefs in self.users.items()
        }

# Global instance
preferences_manager = UserPreferencesManager()