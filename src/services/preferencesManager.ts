import { z } from 'zod';

// Preference schemas
const TradingPreferences = z.object({
  maxPositionSize: z.number().min(0).max(1),
  riskTolerance: z.enum(['low', 'medium', 'high']),
  preferredChains: z.array(z.string()),
  autoTrade: z.boolean(),
  notificationChannels: z.array(z.enum(['email', 'websocket']))
});

const UIPreferences = z.object({
  theme: z.enum(['light', 'dark']),
  chartInterval: z.enum(['1m', '5m', '15m', '1h', '4h', '1d']),
  defaultView: z.enum(['portfolio', 'trading', 'analysis']),
  notificationsEnabled: z.boolean(),
  soundEnabled: z.boolean()
});

const AnalysisPreferences = z.object({
  preferredTimeframes: z.array(z.enum(['1m', '5m', '15m', '1h', '4h', '1d'])),
  indicators: z.array(z.string()),
  emotionAlerts: z.boolean(),
  riskAlerts: z.boolean()
});

const AIPreferences = z.object({
  customStrategies: z.array(z.string()),
  autoOptimize: z.boolean(),
  minConfidence: z.number().min(0).max(1),
  maxRiskLevel: z.enum(['low', 'medium', 'high']),
  tradingStyle: z.enum(['conservative', 'balanced', 'aggressive'])
});

const UserPreferences = z.object({
  trading: TradingPreferences,
  ui: UIPreferences,
  analysis: AnalysisPreferences,
  ai: AIPreferences
});

// Types derived from schemas
export type TradingPrefs = z.infer<typeof TradingPreferences>;
export type UIPrefs = z.infer<typeof UIPreferences>;
export type AnalysisPrefs = z.infer<typeof AnalysisPreferences>;
export type AIPrefs = z.infer<typeof AIPreferences>;
export type UserPrefs = z.infer<typeof UserPreferences>;

// Default preferences
export const defaultPreferences: UserPrefs = {
  trading: {
    maxPositionSize: 0.1,
    riskTolerance: 'medium',
    preferredChains: ['ethereum', 'polygon'],
    autoTrade: false,
    notificationChannels: ['email', 'websocket']
  },
  ui: {
    theme: 'dark',
    chartInterval: '15m',
    defaultView: 'trading',
    notificationsEnabled: true,
    soundEnabled: true
  },
  analysis: {
    preferredTimeframes: ['1h', '4h', '1d'],
    indicators: ['RSI', 'MACD', 'BB'],
    emotionAlerts: true,
    riskAlerts: true
  },
  ai: {
    customStrategies: [],
    autoOptimize: true,
    minConfidence: 0.7,
    maxRiskLevel: 'medium',
    tradingStyle: 'balanced'
  }
};

class PreferencesManager {
  private static instance: PreferencesManager;
  private preferences: Map<string, UserPrefs> = new Map();

  private constructor() {
    // Private constructor for singleton pattern
  }

  public static getInstance(): PreferencesManager {
    if (!PreferencesManager.instance) {
      PreferencesManager.instance = new PreferencesManager();
    }
    return PreferencesManager.instance;
  }

  public async getUserPreferences(userId: string): Promise<UserPrefs> {
    if (!this.preferences.has(userId)) {
      // Load from storage or use defaults
      const stored = localStorage.getItem(`preferences_${userId}`);
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          const validated = UserPreferences.parse(parsed);
          this.preferences.set(userId, validated);
        } catch (err) {
          console.error('Invalid stored preferences, using defaults:', err);
          this.preferences.set(userId, defaultPreferences);
        }
      } else {
        this.preferences.set(userId, defaultPreferences);
      }
    }
    return this.preferences.get(userId)!;
  }

  public async updatePreferences(userId: string, updates: Partial<UserPrefs>): Promise<UserPrefs> {
    const current = await this.getUserPreferences(userId);
    const updated = {
      ...current,
      ...updates,
      trading: { ...current.trading, ...updates.trading },
      ui: { ...current.ui, ...updates.ui },
      analysis: { ...current.analysis, ...updates.analysis },
      ai: { ...current.ai, ...updates.ai }
    };

    // Validate updated preferences
    try {
      const validated = UserPreferences.parse(updated);
      this.preferences.set(userId, validated);
      localStorage.setItem(`preferences_${userId}`, JSON.stringify(validated));
      return validated;
    } catch (err) {
      console.error('Invalid preference update:', err);
      throw new Error('Invalid preference update');
    }
  }

  public async exportPreferences(userId: string): Promise<string> {
    const prefs = await this.getUserPreferences(userId);
    return JSON.stringify(prefs, null, 2);
  }

  public async importPreferences(userId: string, data: string): Promise<boolean> {
    try {
      const parsed = JSON.parse(data);
      const validated = UserPreferences.parse(parsed);
      this.preferences.set(userId, validated);
      localStorage.setItem(`preferences_${userId}`, JSON.stringify(validated));
      return true;
    } catch (err) {
      console.error('Failed to import preferences:', err);
      return false;
    }
  }
}

export const preferencesManager = PreferencesManager.getInstance();