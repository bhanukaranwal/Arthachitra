#include "redis_publisher.h"
#include <iostream>
#include <thread>
#include <chrono>

RedisPublisher::RedisPublisher(const std::string& host, int port, const std::string& password)
    : host_(host), port_(port), password_(password), context_(nullptr), connected_(false) {
}

RedisPublisher::~RedisPublisher() {
    disconnect();
}

bool RedisPublisher::connect() {
    try {
        // Create Redis connection
        struct timeval timeout = { 5, 0 }; // 5 seconds timeout
        context_ = redisConnectWithTimeout(host_.c_str(), port_, timeout);
        
        if (context_ == nullptr || context_->err) {
            if (context_) {
                std::cerr << "Redis connection error: " << context_->errstr << std::endl;
                redisFree(context_);
                context_ = nullptr;
            } else {
                std::cerr << "Redis connection error: can't allocate redis context" << std::endl;
            }
            return false;
        }
        
        // Authenticate if password provided
        if (!password_.empty()) {
            redisReply* reply = (redisReply*)redisCommand(context_, "AUTH %s", password_.c_str());
            if (reply == nullptr || reply->type == REDIS_REPLY_ERROR) {
                std::cerr << "Redis authentication failed" << std::endl;
                if (reply) freeReplyObject(reply);
                redisFree(context_);
                context_ = nullptr;
                return false;
            }
            freeReplyObject(reply);
        }
        
        connected_ = true;
        std::cout << "✅ Connected to Redis at " << host_ << ":" << port_ << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "Redis connection exception: " << e.what() << std::endl;
        return false;
    }
}

void RedisPublisher::disconnect() {
    if (context_) {
        redisFree(context_);
        context_ = nullptr;
        connected_ = false;
        std::cout << "Disconnected from Redis" << std::endl;
    }
}

bool RedisPublisher::publish(const std::string& channel, const std::string& message) {
    if (!connected_ || !context_) {
        std::cerr << "Redis not connected" << std::endl;
        return false;
    }
    
    try {
        redisReply* reply = (redisReply*)redisCommand(
            context_, 
            "PUBLISH %s %s", 
            channel.c_str(), 
            message.c_str()
        );
        
        if (reply == nullptr) {
            std::cerr << "Redis publish failed: connection lost" << std::endl;
            connected_ = false;
            return false;
        }
        
        if (reply->type == REDIS_REPLY_ERROR) {
            std::cerr << "Redis publish error: " << reply->str << std::endl;
            freeReplyObject(reply);
            return false;
        }
        
        int subscribers = reply->integer;
        freeReplyObject(reply);
        
        // Log only if we have subscribers
        if (subscribers > 0) {
            std::cout << "Published to " << subscribers << " subscribers on channel: " << channel << std::endl;
        }
        
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "Redis publish exception: " << e.what() << std::endl;
        return false;
    }
}

bool RedisPublisher::publishOrderBook(const std::string& symbol, const nlohmann::json& orderbook) {
    std::string channel = "orderbook:" + symbol;
    std::string message = orderbook.dump();
    return publish(channel, message);
}

bool RedisPublisher::publishTrade(const std::string& symbol, const nlohmann::json& trade) {
    std::string channel = "trades:" + symbol;
    std::string message = trade.dump();
    return publish(channel, message);
}

bool RedisPublisher::publishQuote(const std::string& symbol, const nlohmann::json& quote) {
    std::string channel = "quotes:" + symbol;
    std::string message = quote.dump();
    return publish(channel, message);
}

bool RedisPublisher::set(const std::string& key, const std::string& value, int expire_seconds) {
    if (!connected_ || !context_) {
        return false;
    }
    
    try {
        redisReply* reply;
        
        if (expire_seconds > 0) {
            reply = (redisReply*)redisCommand(
                context_, 
                "SETEX %s %d %s", 
                key.c_str(), 
                expire_seconds, 
                value.c_str()
            );
        } else {
            reply = (redisReply*)redisCommand(
                context_, 
                "SET %s %s", 
                key.c_str(), 
                value.c_str()
            );
        }
        
        if (reply == nullptr || reply->type == REDIS_REPLY_ERROR) {
            if (reply) freeReplyObject(reply);
            return false;
        }
        
        freeReplyObject(reply);
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "Redis SET exception: " << e.what() << std::endl;
        return false;
    }
}

std::string RedisPublisher::get(const std::string& key) {
    if (!connected_ || !context_) {
        return "";
    }
    
    try {
        redisReply* reply = (redisReply*)redisCommand(context_, "GET %s", key.c_str());
        
        if (reply == nullptr || reply->type != REDIS_REPLY_STRING) {
            if (reply) freeReplyObject(reply);
            return "";
        }
        
        std::string value(reply->str, reply->len);
        freeReplyObject(reply);
        return value;
        
    } catch (const std::exception& e) {
        std::cerr << "Redis GET exception: " << e.what() << std::endl;
        return "";
    }
}

bool RedisPublisher::ping() {
    if (!connected_ || !context_) {
        return false;
    }
    
    try {
        redisReply* reply = (redisReply*)redisCommand(context_, "PING");
        
        if (reply == nullptr || reply->type != REDIS_REPLY_STATUS) {
            if (reply) freeReplyObject(reply);
            return false;
        }
        
        bool success = (strcmp(reply->str, "PONG") == 0);
        freeReplyObject(reply);
        return success;
        
    } catch (const std::exception& e) {
        std::cerr << "Redis PING exception: " << e.what() << std::endl;
        return false;
    }
}

void RedisPublisher::startHeartbeat(int interval_seconds) {
    heartbeat_thread_ = std::thread([this, interval_seconds]() {
        while (connected_) {
            if (!ping()) {
                std::cerr << "Redis heartbeat failed, attempting to reconnect..." << std::endl;
                connected_ = false;
                
                // Attempt reconnection
                std::this_thread::sleep_for(std::chrono::seconds(5));
                if (connect()) {
                    std::cout << "Redis reconnected successfully" << std::endl;
                }
            }
            
            std::this_thread::sleep_for(std::chrono::seconds(interval_seconds));
        }
    });
}

void RedisPublisher::stopHeartbeat() {
    if (heartbeat_thread_.joinable()) {
        connected_ = false;
        heartbeat_thread_.join();
    }
}
