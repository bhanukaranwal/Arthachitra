// RSI Mean Reversion Strategy
// VedaScript Example

var rsi_period = 14
var oversold_level = 30
var overbought_level = 70

function checkRSISignals() {
    var rsi_value = rsi(rsi_period)
    var pos = position()
    
    // Oversold condition - potential buy
    if (rsi_value < oversold_level and rsi_value[1] >= oversold_level) {
        if (pos.quantity == 0) {
            buy("RSI Oversold Entry", 50)
        }
    }
    
    // Overbought condition - potential sell
    if (rsi_value > overbought_level and rsi_value[1] <= overbought_level) {
        if (pos.quantity > 0) {
            sell("RSI Overbought Exit", pos.quantity)
        }
    }
}

// Risk management
function checkStopLoss() {
    var pos = position()
    var current_price = close()
    
    if (pos.quantity > 0) {
        var stop_loss_price = pos.average_price * 0.95  // 5% stop loss
        if (current_price < stop_loss_price) {
            sell("Stop Loss Hit", pos.quantity)
        }
    }
}

// Main execution
function main() {
    checkRSISignals()
    checkStopLoss()
}

main()
