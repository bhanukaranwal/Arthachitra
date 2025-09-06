#include <gtest/gtest.h>
#include "order_book.h"

class OrderBookTest : public ::testing::Test {
protected:
    void SetUp() override {
        orderbook = std::make_unique<OrderBook>("TEST");
    }
    
    std::unique_ptr<OrderBook> orderbook;
};

TEST_F(OrderBookTest, InitialState) {
    EXPECT_EQ(orderbook->getSymbol(), "TEST");
    EXPECT_EQ(orderbook->getBestBid(), 0.0);
    EXPECT_EQ(orderbook->getBestAsk(), 0.0);
    EXPECT_EQ(orderbook->getSpread(), 0.0);
}

TEST_F(OrderBookTest, UpdateBids) {
    orderbook->updateBid(100.0, 1000);
    orderbook->updateBid(99.5, 500);
    orderbook->updateBid(101.0, 200);
    
    EXPECT_EQ(orderbook->getBestBid(), 101.0);
    
    auto bids = orderbook->getBids(3);
    ASSERT_EQ(bids.size(), 3);
    EXPECT_EQ(bids[0].price, 101.0);
    EXPECT_EQ(bids[1].price, 100.0);
    EXPECT_EQ(bids[2].price, 99.5);
}

TEST_F(OrderBookTest, UpdateAsks) {
    orderbook->updateAsk(102.0, 800);
    orderbook->updateAsk(103.0, 600);
    orderbook->updateAsk(101.5, 400);
    
    EXPECT_EQ(orderbook->getBestAsk(), 101.5);
    
    auto asks = orderbook->getAsks(3);
    ASSERT_EQ(asks.size(), 3);
    EXPECT_EQ(asks[0].price, 101.5);
    EXPECT_EQ(asks[1].price, 102.0);
    EXPECT_EQ(asks[2].price, 103.0);
}

TEST_F(OrderBookTest, SpreadCalculation) {
    orderbook->updateBid(100.0, 1000);
    orderbook->updateAsk(102.0, 800);
    
    EXPECT_EQ(orderbook->getSpread(), 2.0);
}

TEST_F(OrderBookTest, RemoveLevel) {
    orderbook->updateBid(100.0, 1000);
    orderbook->updateBid(100.0, 0); // Remove level
    
    EXPECT_EQ(orderbook->getBestBid(), 0.0);
}

TEST_F(OrderBookTest, JsonSerialization) {
    orderbook->updateBid(100.0, 1000);
    orderbook->updateAsk(102.0, 800);
    
    auto json = orderbook->toJson(5);
    
    EXPECT_EQ(json["symbol"], "TEST");
    EXPECT_EQ(json["spread"], 2.0);
    EXPECT_EQ(json["bids"].size(), 1);
    EXPECT_EQ(json["asks"].size(), 1);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
