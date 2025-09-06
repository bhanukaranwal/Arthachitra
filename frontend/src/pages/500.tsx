import React from 'react';
import Link from 'next/link';
import { Header } from '../components/ui/Header';

const ServerErrorPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="max-w-lg mx-auto text-center">
          <div className="mb-8">
            <h1 className="text-9xl font-bold text-red-300 dark:text-red-600">500</h1>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              Server Error
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-8">
              Something went wrong on our end. We're working to fix it.
            </p>
          </div>
          
          <div className="space-y-4">
            <Link
              href="/"
              className="inline-block px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Try Again
            </Link>
            <div>
              <button
                onClick={() => window.location.reload()}
                className="text-red-600 hover:text-red-500 mx-4"
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ServerErrorPage;
