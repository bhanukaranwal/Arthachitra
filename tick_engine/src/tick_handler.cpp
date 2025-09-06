#include "tick_handler.h"
#include "redis_publisher.h"
#include <iostream>
#include <chrono>
#include <thread>
#include <random>

TickHandler::TickHandler() : running_(false) {
    redis_publisher_ = std::make_unique<RedisPublisher>("localhost", 6379);
}

TickHandler::~TickHandler() {
    stop();
}

void TickHandler::start() {
    if (running_) return;
    
    running_ = true;
    tick_thread_ = std::thread(&TickHandler::tickLoop, this);
    std::cout << "Tick engine started" << std::endl;
}

void TickHandler::stop() {
    if (!running_) return;
    
    running_ = false;
    if (tick_thread_.joinable()) {
        tick_thread_.join();
    }
    std::cout << "Tick engine stopped" << std::endl;
}

void TickHandler::processOrderBookUpdate(const std::string& symbol, const OrderBookUpdate& update) {
    std::lock_guard<std::mutex> lock(orderbook_mutex_);
    
    auto& orderbook = orderbooks_[symbol];
    
    if (update.side == Side::BUY) {
        if (update.action == Action::ADD || update.action == Action::UPDATE) {
            orderbook.bids[update.price] = update.quantity;
        } else if (update.action == Action::DELETE) {
            orderbook.bids.erase(update.price);
        }
    } else {
        if (update.action == Action::ADD || update.action == Action::UPDATE) {
            orderbook.asks[update.price] = update.quantity;
        } else if (update.action == Action::DELETE) {
            orderbook.asks.erase(update.price);
        }
    }
    
    // Publish to Redis
    publishOrderBook(symbol, orderbook);
}

void TickHandler::processTrade(const std::string& symbol, const Trade& trade) {
    std::lock_guard<std::mutex> lock(trades_mutex_);
    
    trades_[symbol].push_back(trade);
    
    // Keep only last 1000 trades per symbol
    if (trades_[symbol].size() > 1000) {
        trades_[symbol].erase(trades_[symbol].begin());
    }
    
    // Publish to Redis
    publishTrade(symbol, trade);
}

void TickHandler::tickLoop() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> price_dist(99.0, 101.0);
    std::uniform_int_distribution<> qty_dist(100, 10000);
    std::uniform_int_distribution<> side_dist(0, 1);
    
    while (running_) {
        // Simulate order book updates for NIFTY
        OrderBookUpdate update;
        update.symbol = "NIFTY";
        update.price = price_dist(gen);
        update.quantity = qty_dist(gen);
        update.side = side_dist(gen) ? Side::BUY : Side::SELL;
        update.action = Action::UPDATE;
        update.timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        
        processOrderBookUpdate("NIFTY", update);
        
        // Simulate trades
        if (qty_dist(gen) % 10 == 0) {  // 10% chance of trade
            Trade trade;
            trade.symbol = "NIFTY";
            trade.price = price_dist(gen);
            trade.quantity = qty_dist(gen) / 10;
            trade.side = side_dist(gen) ? Side::BUY : Side::SELL;
            trade.timestamp = update.timestamp;
            
            processTrade("NIFTY", trade);
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(10));  // 100 updates per second
    }
}

void TickHandler::publishOrderBook(const std::string& symbol, const OrderBook& orderbook) {
    // Convert to JSON and publish
    std::string json = "{\"type\":\"orderbook\",\"symbol\":\"" + symbol + "\",";
    json += "\"bids\":[";
    
    bool first = true;
    for (const auto& bid : orderbook.bids) {
        if (!first) json += ",";
        json += "{\"price\":" + std::to_string(bid.first) + ",\"size\":" + std::to_string(bid.second) + "}";
        first = false;
    }
    
    json += "],\"asks\":[";
    first = true;
    for (const auto& ask : orderbook.asks) {
        if (!first) json += ",";
        json += "{\"price\":" + std::to_string(ask.first) + ",\"size\":" + std::to_string(ask.second) + "}";
        first = false;
    }
    
    json += "]}";
    
    redis_publisher_->publish("orderbook:" + symbol, json);
}

void TickHandler::publishTrade(const std::string& symbol, const Trade& trade) {
    std::string json = "{\"type\":\"trade\",\"symbol\":\"" + symbol + "\",";
    json += "\"price\":" + std::to_string(trade.price) + ",";
    json += "\"quantity\":" + std::to_string(trade.quantity) + ",";
    json += "\"side\":\"" + (trade.side == Side::BUY ? "buy" : "sell") + "\",";
    json += "\"timestamp\":" + std::to_string(trade.timestamp) + "}";
    
    redis_publisher_->publish("trades:" + symbol, json);
}
