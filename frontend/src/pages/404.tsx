import React from 'react';
import Link from 'next/link';
import { Header } from '../components/ui/Header';

const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="max-w-lg mx-auto text-center">
          <div className="mb-8">
            <h1 className="text-9xl font-bold text-gray-300 dark:text-gray-600">404</h1>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              Page Not Found
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-8">
              The page you're looking for doesn't exist or has been moved.
            </p>
          </div>
          
          <div className="space-y-4">
            <Link
              href="/"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go Home
            </Link>
            <div>
              <Link
                href="/portfolio"
                className="text-blue-600 hover:text-blue-500 mx-4"
              >
                Portfolio
              </Link>
              <Link
                href="/orders"
                className="text-blue-600 hover:text-blue-500 mx-4"
              >
                Orders
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
