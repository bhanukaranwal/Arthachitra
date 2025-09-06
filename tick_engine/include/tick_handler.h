#ifndef TICK_HANDLER_H
#define TICK_HANDLER_H

#include <memory>
#include <thread>
#include <atomic>
#include <unordered_map>
#include <mutex>
#include <vector>
#include <string>

enum class Side {
    BUY,
    SELL
};

enum class Action {
    ADD,
    UPDATE,
    DELETE
};

struct OrderBookUpdate {
    std::string symbol;
    double price;
    int quantity;
    Side side;
    Action action;
    long long timestamp;
};

struct Trade {
    std::string symbol;
    double price;
    int quantity;
    Side side;
    long long timestamp;
};

struct OrderBook {
    std::map<double, int> bids;   // price -> quantity
    std::map<double, int> asks;   // price -> quantity
};

class RedisPublisher;

class TickHandler {
public:
    TickHandler();
    ~TickHandler();
    
    void start();
    void stop();
    
    void processOrderBookUpdate(const std::string& symbol, const OrderBookUpdate& update);
    void processTrade(const std::string& symbol, const Trade& trade);
    
    bool isRunning() const { return running_; }
    
private:
    void tickLoop();
    void publishOrderBook(const std::string& symbol, const OrderBook& orderbook);
    void publishTrade(const std::string& symbol, const Trade& trade);
    
    std::atomic<bool> running_;
    std::thread tick_thread_;
    
    std::unordered_map<std::string, OrderBook> orderbooks_;
    std::unordered_map<std::string, std::vector<Trade>> trades_;
    
    std::mutex orderbook_mutex_;
    std::mutex trades_mutex_;
    
    std::unique_ptr<RedisPublisher> redis_publisher_;
};

#endif // TICK_HANDLER_H
