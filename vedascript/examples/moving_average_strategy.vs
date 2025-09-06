// VedaScript Moving Average Crossover Strategy
// This strategy buys when fast MA crosses above slow MA and sells when it crosses below

function movingAverageCrossover() {
    var fastPeriod = 10;
    var slowPeriod = 20;
    var position = 0;
    
    // Calculate moving averages
    var fastMA = sma(close, fastPeriod);
    var slowMA = sma(close, slowPeriod);
    
    // Previous values for crossover detection
    var prevFastMA = fastMA[1];
    var prevSlowMA = slowMA[1];
    
    // Entry conditions
    if (fastMA > slowMA and prevFastMA <= prevSlowMA) {
        // Bullish crossover - Buy signal
        if (position <= 0) {
            buy("Entry: MA Bullish Crossover");
            position = 1;
        }
    }
    
    if (fastMA < slowMA and prevFastMA >= prevSlowMA) {
        // Bearish crossover - Sell signal
        if (position >= 0) {
            sell("Exit: MA Bearish Crossover");
            position = -1;
        }
    }
    
    // Risk management
    var stopLoss = 0.02; // 2% stop loss
    var takeProfit = 0.04; // 4% take profit
    
    if (position > 0) {
        var entryPrice = strategy.position_avg_price;
        var currentPrice = close;
        
        if (currentPrice <= entryPrice * (1 - stopLoss)) {
            sell("Stop Loss Hit");
            position = 0;
        }
        
        if (currentPrice >= entryPrice * (1 + takeProfit)) {
            sell("Take Profit Hit");
            position = 0;
        }
    }
    
    return position;
}

// Plot indicators on chart
plot(sma(close, 10), "Fast MA", color.blue);
plot(sma(close, 20), "Slow MA", color.red);

// Execute strategy
movingAverageCrossover();
