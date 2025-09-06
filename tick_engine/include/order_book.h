#ifndef ORDER_BOOK_H
#define ORDER_BOOK_H

#include <map>
#include <vector>
#include <string>
#include <mutex>
#include <chrono>
#include <nlohmann/json.hpp>

struct OrderBookLevel {
    double price;
    int quantity;
};

class OrderBook {
public:
    OrderBook(const std::string& symbol);
    
    void updateBid(double price, int quantity);
    void updateAsk(double price, int quantity);
    
    double getBestBid() const;
    double getBestAsk() const;
    double getSpread() const;
    
    std::vector<OrderBookLevel> getBids(int depth = 10) const;
    std::vector<OrderBookLevel> getAsks(int depth = 10) const;
    
    nlohmann::json toJson(int depth = 10) const;
    
    const std::string& getSymbol() const { return symbol_; }

private:
    std::string symbol_;
    std::map<double, int> bids_;   // price -> quantity (sorted ascending)
    std::map<double, int> asks_;   // price -> quantity (sorted ascending)
    mutable std::mutex mutex_;
    std::chrono::high_resolution_clock::time_point last_updated_;
};

#endif // ORDER_BOOK_H
