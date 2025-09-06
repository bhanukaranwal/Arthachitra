import React, { createContext, useContext, useEffect, useState } from 'react';
import { ThemeConfig, Theme } from '../../types/theme';

interface ThemeContextType {
  theme: Theme;
  themeName: string;
  setTheme: (themeName: string) => void;
  availableThemes: string[];
  customThemes: ThemeConfig[];
  addCustomTheme: (theme: ThemeConfig) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const defaultThemes: Record<string, Theme> = {
  'modern-light': {
    name: 'Modern Light',
    colors: {
      primary: '#1f2937',
      secondary: '#374151',
      accent: '#3b82f6',
      background: '#ffffff',
      surface: '#f9fafb',
      text: '#111827',
      textSecondary: '#6b7280',
      border: '#e5e7eb',
      success: '#10b981',
      error: '#ef4444',
      warning: '#f59e0b'
    },
    chart: {
      background: '#ffffff',
      gridColor: '#f3f4f6',
      textColor: '#374151',
      borderColor: '#d1d5db',
      upColor: '#10b981',
      downColor: '#ef4444',
      volumeColor: '#9ca3af',
      crosshairColor: '#6b7280'
    },
    orderbook: {
      bidColor: '#dcfce7',
      askColor: '#fee2e2',
      bidTextColor: '#166534',
      askTextColor: '#991b1b',
      spreadColor: '#fef3c7'
    }
  },
  'dark-pro': {
    name: 'Dark Pro',
    colors: {
      primary: '#f8fafc',
      secondary: '#e2e8f0',
      accent: '#3b82f6',
      background: '#0f172a',
      surface: '#1e293b',
      text: '#f1f5f9',
      textSecondary: '#94a3b8',
      border: '#334155',
      success: '#22c55e',
      error: '#ef4444',
      warning: '#eab308'
    },
    chart: {
      background: '#0f172a',
      gridColor: '#1e293b',
      textColor: '#cbd5e1',
      borderColor: '#475569',
      upColor: '#22c55e',
      downColor: '#ef4444',
      volumeColor: '#64748b',
      crosshairColor: '#94a3b8'
    },
    orderbook: {
      bidColor: '#065f46',
      askColor: '#7f1d1d',
      bidTextColor: '#34d399',
      askTextColor: '#f87171',
      spreadColor: '#451a03'
    }
  },
  'rangoli': {
    name: 'Rangoli Festival',
    colors: {
      primary: '#7c3aed',
      secondary: '#a855f7',
      accent: '#ec4899',
      background: '#fef7ff',
      surface: '#faf5ff',
      text: '#581c87',
      textSecondary: '#7c2d92',
      border: '#d8b4fe',
      success: '#059669',
      error: '#dc2626',
      warning: '#d97706'
    },
    chart: {
      background: '#fef7ff',
      gridColor: '#f3e8ff',
      textColor: '#6b21a8',
      borderColor: '#c4b5fd',
      upColor: '#059669',
      downColor: '#dc2626',
      volumeColor: '#8b5cf6',
      crosshairColor: '#a855f7'
    },
    orderbook: {
      bidColor: '#d1fae5',
      askColor: '#fecaca',
      bidTextColor: '#047857',
      askTextColor: '#b91c1c',
      spreadColor: '#fef3c7'
    }
  },
  'diwali-glow': {
    name: 'Diwali Glow',
    colors: {
      primary: '#92400e',
      secondary: '#b45309',
      accent: '#f59e0b',
      background: '#fffbeb',
      surface: '#fef3c7',
      text: '#78350f',
      textSecondary: '#92400e',
      border: '#fcd34d',
      success: '#059669',
      error: '#dc2626',
      warning: '#d97706'
    },
    chart: {
      background: '#fffbeb',
      gridColor: '#fef3c7',
      textColor: '#92400e',
      borderColor: '#fcd34d',
      upColor: '#059669',
      downColor: '#dc2626',
      volumeColor: '#d97706',
      crosshairColor: '#b45309'
    },
    orderbook: {
      bidColor: '#d1fae5',
      askColor: '#fecaca',
      bidTextColor: '#047857',
      askTextColor: '#b91c1c',
      spreadColor: '#fed7aa'
    }
  }
};

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [themeName, setThemeName] = useState('modern-light');
  const [customThemes, setCustomThemes] = useState<ThemeConfig[]>([]);

  useEffect(() => {
    const savedTheme = localStorage.getItem('arthachitra-theme');
    const savedCustomThemes = localStorage.getItem('arthachitra-custom-themes');
    
    if (savedTheme) {
      setThemeName(savedTheme);
    }
    
    if (savedCustomThemes) {
      try {
        setCustomThemes(JSON.parse(savedCustomThemes));
      } catch (error) {
        console.error('Failed to parse custom themes:', error);
      }
    }
  }, []);

  const setTheme = (newThemeName: string) => {
    setThemeName(newThemeName);
    localStorage.setItem('arthachitra-theme', newThemeName);
    
    // Apply CSS custom properties
    const theme = getCurrentTheme(newThemeName);
    applyThemeToDOM(theme);
  };

  const getCurrentTheme = (name: string): Theme => {
    if (defaultThemes[name]) {
      return defaultThemes[name];
    }
    
    const customTheme = customThemes.find(t => t.name === name);
    if (customTheme) {
      return customTheme.theme;
    }
    
    return defaultThemes['modern-light'];
  };

  const applyThemeToDOM = (theme: Theme) => {
    const root = document.documentElement;
    
    // Apply color variables
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });
    
    // Apply chart variables
    Object.entries(theme.chart).forEach(([key, value]) => {
      root.style.setProperty(`--chart-${key}`, value);
    });
    
    // Apply orderbook variables
    Object.entries(theme.orderbook).forEach(([key, value]) => {
      root.style.setProperty(`--orderbook-${key}`, value);
    });
  };

  const addCustomTheme = (themeConfig: ThemeConfig) => {
    const newCustomThemes = [...customThemes, themeConfig];
    setCustomThemes(newCustomThemes);
    localStorage.setItem('arthachitra-custom-themes', JSON.stringify(newCustomThemes));
  };

  const availableThemes = [...Object.keys(defaultThemes), ...customThemes.map(t => t.name)];

  useEffect(() => {
    applyThemeToDOM(getCurrentTheme(themeName));
  }, [themeName, customThemes]);

  return (
    <ThemeContext.Provider value={{
      theme: getCurrentTheme(themeName),
      themeName,
      setTheme,
      availableThemes,
      customThemes,
      addCustomTheme
    }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
