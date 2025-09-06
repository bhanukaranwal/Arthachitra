import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const menuItems = [
  { name: 'Dashboard', href: '/', icon: '📊' },
  { name: 'Charts', href: '/charts', icon: '📈' },
  { name: 'Order Flow', href: '/orderflow', icon: '🔥' },
  { name: 'Portfolio', href: '/portfolio', icon: '💼' },
  { name: 'Orders', href: '/orders', icon: '📋' },
  { name: 'Strategies', href: '/strategies', icon: '🤖' },
  { name: 'Brokers', href: '/brokers', icon: '🏦' },
  { name: 'Settings', href: '/settings', icon: '⚙️' },
];

export const Sidebar: React.FC = () => {
  const router = useRouter();

  return (
    <div className="w-64 bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700">
      <nav className="mt-5 px-2">
        <div className="space-y-1">
          {menuItems.map((item) => {
            const isActive = router.pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                  isActive
                    ? 'bg-blue-100 text-blue-900 dark:bg-blue-800 dark:text-blue-100'
                    : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                }`}
              >
                <span className="mr-3 text-lg">{item.icon}</span>
                {item.name}
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
};
