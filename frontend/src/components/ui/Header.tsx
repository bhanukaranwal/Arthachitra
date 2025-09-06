import React from 'react';
import { useAppSelector, useAppDispatch } from '../../store';
import { logout } from '../../store/authSlice';
import { ThemeSwitcher } from '../themes/ThemeSwitcher';

export const Header: React.FC = () => {
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const dispatch = useAppDispatch();

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Arthachitra
          </h1>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            अर्थचित्र
          </span>
        </div>

        <div className="flex items-center space-x-4">
          <ThemeSwitcher />
          
          {isAuthenticated ? (
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Welcome, {user?.username}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          ) : (
            <a
              href="/login"
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Login
            </a>
          )}
        </div>
      </div>
    </header>
  );
};
