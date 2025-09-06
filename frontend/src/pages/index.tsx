import React from 'react';
import Head from 'next/head';
import { CandlestickChart } from '../components/charts/CandlestickChart';
import { HeatmapChart } from '../components/charts/HeatmapChart';
import { OrderBookLadder } from '../components/orderbook/OrderBookLadder';
import { Header } from '../components/ui/Header';
import { Sidebar } from '../components/ui/Sidebar';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Head>
        <title>Arthachitra - Next-Generation Trading Platform</title>
        <meta name="description" content="Advanced trading platform with order flow analysis" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="flex h-screen">
        <Sidebar />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          
          <main className="flex-1 overflow-hidden bg-white dark:bg-gray-800">
            <div className="h-full grid grid-cols-12 gap-4 p-4">
              {/* Main Chart Area */}
              <div className="col-span-8">
                <div className="h-full grid grid-rows-2 gap-4">
                  <CandlestickChart symbol="NIFTY" timeframe="1d" />
                  <HeatmapChart symbol="NIFTY" />
                </div>
              </div>
              
              {/* Order Book */}
              <div className="col-span-4">
                <OrderBookLadder 
                  symbol="NIFTY" 
                  onPriceClick={(price, side) => {
                    console.log(`Price clicked: ${price} (${side})`);
                  }}
                />
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
