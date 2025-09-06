// Simple Moving Average Crossover Strategy
// VedaScript Example

function main() {
    var sma_fast = sma(10)
    var sma_slow = sma(20)
    var current_position = position()
    
    // Entry conditions
    if (sma_fast > sma_slow and sma_fast[1] <= sma_slow[1]) {
        if (current_position.quantity <= 0) {
            buy("SMA Crossover Buy Signal", 100)
        }
    }
    
    // Exit conditions
    if (sma_fast < sma_slow and sma_fast[1] >= sma_slow[1]) {
        if (current_position.quantity > 0) {
            sell("SMA Crossover Sell Signal", current_position.quantity)
        }
    }
}

// Entry point
main()
