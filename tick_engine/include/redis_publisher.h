#ifndef REDIS_PUBLISHER_H
#define REDIS_PUBLISHER_H

#include <string>
#include <hiredis/hiredis.h>
#include <nlohmann/json.hpp>
#include <thread>
#include <atomic>

class RedisPublisher {
public:
    RedisPublisher(const std::string& host = "localhost", int port = 6379, const std::string& password = "");
    ~RedisPublisher();
    
    bool connect();
    void disconnect();
    bool isConnected() const { return connected_; }
    
    bool publish(const std::string& channel, const std::string& message);
    bool publishOrderBook(const std::string& symbol, const nlohmann::json& orderbook);
    bool publishTrade(const std::string& symbol, const nlohmann::json& trade);
    bool publishQuote(const std::string& symbol, const nlohmann::json& quote);
    
    bool set(const std::string& key, const std::string& value, int expire_seconds = 0);
    std::string get(const std::string& key);
    bool ping();
    
    void startHeartbeat(int interval_seconds = 30);
    void stopHeartbeat();

private:
    std::string host_;
    int port_;
    std::string password_;
    redisContext* context_;
    std::atomic<bool> connected_;
    std::thread heartbeat_thread_;
};

#endif // REDIS_PUBLISHER_H
