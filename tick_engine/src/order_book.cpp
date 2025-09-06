#include "order_book.h"
#include <algorithm>
#include <iostream>

OrderBook::OrderBook(const std::string& symbol) : symbol_(symbol) {
    // Initialize empty order book
}

void OrderBook::updateBid(double price, int quantity) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    if (quantity > 0) {
        bids_[price] = quantity;
    } else {
        bids_.erase(price);
    }
    
    last_updated_ = std::chrono::high_resolution_clock::now();
}

void OrderBook::updateAsk(double price, int quantity) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    if (quantity > 0) {
        asks_[price] = quantity;
    } else {
        asks_.erase(price);
    }
    
    last_updated_ = std::chrono::high_resolution_clock::now();
}

double OrderBook::getBestBid() const {
    std::lock_guard<std::mutex> lock(mutex_);
    if (bids_.empty()) return 0.0;
    return bids_.rbegin()->first; // Highest bid
}

double OrderBook::getBestAsk() const {
    std::lock_guard<std::mutex> lock(mutex_);
    if (asks_.empty()) return 0.0;
    return asks_.begin()->first; // Lowest ask
}

double OrderBook::getSpread() const {
    double bid = getBestBid();
    double ask = getBestAsk();
    return (bid > 0 && ask > 0) ? ask - bid : 0.0;
}

std::vector<OrderBookLevel> OrderBook::getBids(int depth) const {
    std::lock_guard<std::mutex> lock(mutex_);
    std::vector<OrderBookLevel> result;
    
    auto it = bids_.rbegin(); // Start from highest bid
    for (int i = 0; i < depth && it != bids_.rend(); ++i, ++it) {
        result.push_back({it->first, it->second});
    }
    
    return result;
}

std::vector<OrderBookLevel> OrderBook::getAsks(int depth) const {
    std::lock_guard<std::mutex> lock(mutex_);
    std::vector<OrderBookLevel> result;
    
    auto it = asks_.begin(); // Start from lowest ask
    for (int i = 0; i < depth && it != asks_.end(); ++i, ++it) {
        result.push_back({it->first, it->second});
    }
    
    return result;
}

nlohmann::json OrderBook::toJson(int depth) const {
    nlohmann::json j;
    j["symbol"] = symbol_;
    j["timestamp"] = std::chrono::duration_cast<std::chrono::milliseconds>(
        last_updated_.time_since_epoch()
    ).count();
    
    // Add bids
    auto bids = getBids(depth);
    for (const auto& level : bids) {
        j["bids"].push_back({level.price, level.quantity});
    }
    
    // Add asks
    auto asks = getAsks(depth);
    for (const auto& level : asks) {
        j["asks"].push_back({level.price, level.quantity});
    }
    
    j["spread"] = getSpread();
    
    return j;
}
