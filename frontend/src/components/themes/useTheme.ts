import { useContext } from 'react';
import { ThemeContext } from './ThemeProvider';

export const useTheme = () => {
  const context = useContext(ThemeContext);
  
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  
  return context;
};

// Additional theme utilities
export const getThemeColors = (themeName: string) => {
  // This could be used to get theme colors without context
  // Useful for components that need theme colors but can't use context
};

export const isLightTheme = (themeName: string): boolean => {
  return themeName === 'light' || themeName === 'diwali';
};

export const isDarkTheme = (themeName: string): boolean => {
  return themeName === 'dark';
};
