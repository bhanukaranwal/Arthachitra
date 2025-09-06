#include <iostream>
#include <thread>
#include <signal.h>
#include <unistd.h>
#include "tick_handler.h"
#include "redis_publisher.h"

volatile bool running = true;

void signalHandler(int signum) {
    std::cout << "\nInterrupt signal (" << signum << ") received.\n";
    running = false;
}

int main(int argc, char* argv[]) {
    // Register signal handler
    signal(SIGINT, signalHandler);
    signal(SIGTERM, signalHandler);
    
    std::cout << "🚀 Starting Arthachitra Tick Engine..." << std::endl;
    
    try {
        // Initialize tick handler
        TickHandler tickHandler;
        
        // Start the tick processing loop
        tickHandler.start();
        
        std::cout << "✅ Tick engine started successfully!" << std::endl;
        std::cout << "Processing market data... Press Ctrl+C to stop." << std::endl;
        
        // Keep running until signal received
        while (running && tickHandler.isRunning()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
        
        std::cout << "🛑 Shutting down tick engine..." << std::endl;
        tickHandler.stop();
        
    } catch (const std::exception& e) {
        std::cerr << "❌ Fatal error: " << e.what() << std::endl;
        return 1;
    }
    
    std::cout << "✅ Tick engine shutdown complete." << std::endl;
    return 0;
}
