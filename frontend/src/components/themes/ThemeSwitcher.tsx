import React from 'react';
import { useTheme } from './ThemeProvider';
import { ChevronDownIcon } from '@heroicons/react/20/solid';
import clsx from 'clsx';

interface ThemeSwitcherProps {
  className?: string;
  compact?: boolean;
}

export const ThemeSwitcher: React.FC<ThemeSwitcherProps> = ({ 
  className = '', 
  compact = false 
}) => {
  const { theme, setTheme, availableThemes } = useTheme();

  const handleThemeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setTheme(event.target.value);
  };

  if (compact) {
    return (
      <div className={clsx('relative', className)}>
        <select
          value={theme.name}
          onChange={handleThemeChange}
          className={clsx(
            'appearance-none bg-transparent border border-gray-300 dark:border-gray-600',
            'rounded-md px-3 py-2 text-sm font-medium',
            'text-gray-700 dark:text-gray-300',
            'hover:border-gray-400 dark:hover:border-gray-500',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'cursor-pointer'
          )}
          aria-label="Select theme"
        >
          {availableThemes.map((t) => (
            <option key={t.name} value={t.name}>
              {t.displayName}
            </option>
          ))}
        </select>
        <ChevronDownIcon className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
      </div>
    );
  }

  return (
    <div className={clsx('theme-switcher', className)}>
      <label htmlFor="theme-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Choose Theme
      </label>
      
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {availableThemes.map((t) => (
          <div
            key={t.name}
            onClick={() => setTheme(t.name)}
            className={clsx(
              'relative cursor-pointer rounded-lg p-3 border-2 transition-all duration-200',
              'hover:shadow-md hover:scale-105',
              theme.name === t.name
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            )}
          >
            {/* Theme Preview */}
            <div className="flex items-center space-x-3">
              <div className="flex space-x-1">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: t.colors.primary }}
                />
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: t.colors.secondary }}
                />
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: t.colors.accent }}
                />
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {t.displayName}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {getThemeDescription(t.name)}
                </p>
              </div>
            </div>
            
            {/* Selected indicator */}
            {theme.name === t.name && (
              <div className="absolute top-2 right-2">
                <div className="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                  <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// Helper function to get theme descriptions
function getThemeDescription(themeName: string): string {
  const descriptions: Record<string, string> = {
    light: 'Clean and professional',
    dark: 'Easy on the eyes',
    rangoli: 'Colorful Indian festival',
    diwali: 'Warm golden glow',
  };
  
  return descriptions[themeName] || 'Custom theme';
}

// Theme preview component for advanced theme switcher
export const ThemePreview: React.FC<{ theme: any }> = ({ theme }) => {
  return (
    <div className="w-full h-24 rounded-md overflow-hidden border border-gray-200 dark:border-gray-700">
      <div className="h-full flex">
        {/* Sidebar preview */}
        <div 
          className="w-1/4 h-full"
          style={{ backgroundColor: theme.colors.surface }}
        >
          <div className="p-2">
            <div 
              className="w-full h-2 rounded mb-1"
              style={{ backgroundColor: theme.colors.primary }}
            />
            <div 
              className="w-3/4 h-1 rounded mb-1"
              style={{ backgroundColor: theme.colors.textSecondary }}
            />
            <div 
              className="w-1/2 h-1 rounded"
              style={{ backgroundColor: theme.colors.textSecondary }}
            />
          </div>
        </div>
        
        {/* Main content preview */}
        <div 
          className="flex-1 h-full"
          style={{ backgroundColor: theme.colors.background }}
        >
          <div className="p-2">
            <div 
              className="w-full h-3 rounded mb-2"
              style={{ backgroundColor: theme.colors.surface }}
            />
            <div className="flex space-x-1 mb-2">
              <div 
                className="w-8 h-2 rounded"
                style={{ backgroundColor: theme.colors.chartUpColor }}
              />
              <div 
                className="w-8 h-2 rounded"
                style={{ backgroundColor: theme.colors.chartDownColor }}
              />
            </div>
            <div 
              className="w-full h-8 rounded"
              style={{ backgroundColor: theme.colors.surface }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
