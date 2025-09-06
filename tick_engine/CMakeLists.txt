cmake_minimum_required(VERSION 3.16)
project(ArthachitiraTickEngine VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimization flags
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -DNDEBUG")
elseif(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -O0 -DDEBUG")
endif()

# Find packages
find_package(Threads REQUIRED)

# Try to find Redis++ (hiredis)
find_path(HIREDIS_INCLUDE_DIR hiredis/hiredis.h)
find_library(HIREDIS_LIBRARY hiredis)

if(NOT HIREDIS_INCLUDE_DIR OR NOT HIREDIS_LIBRARY)
    message(STATUS "hiredis not found, downloading and building...")
    
    include(FetchContent)
    FetchContent_Declare(
        hiredis
        GIT_REPOSITORY https://github.com/redis/hiredis.git
        GIT_TAG v1.2.0
    )
    FetchContent_MakeAvailable(hiredis)
    set(HIREDIS_LIBRARY hiredis)
endif()

# Find nlohmann/json
find_package(nlohmann_json QUIET)
if(NOT nlohmann_json_FOUND)
    message(STATUS "nlohmann/json not found, downloading...")
    
    FetchContent_Declare(
        nlohmann_json
        GIT_REPOSITORY https://github.com/nlohmann/json.git
        GIT_TAG v3.11.2
    )
    FetchContent_MakeAvailable(nlohmann_json)
endif()

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
if(HIREDIS_INCLUDE_DIR)
    include_directories(${HIREDIS_INCLUDE_DIR})
endif()

# Source files
set(SOURCES
    src/main.cpp
    src/tick_handler.cpp
    src/order_book.cpp
    src/redis_publisher.cpp
)

# Header files
set(HEADERS
    include/tick_handler.h
    include/order_book.h
    include/redis_publisher.h
)

# Create executable
add_executable(tick_engine ${SOURCES} ${HEADERS})

# Link libraries
target_link_libraries(tick_engine 
    PRIVATE 
    Threads::Threads
    ${HIREDIS_LIBRARY}
)

if(TARGET nlohmann_json::nlohmann_json)
    target_link_libraries(tick_engine PRIVATE nlohmann_json::nlohmann_json)
endif()

# Compiler-specific options
if(MSVC)
    target_compile_options(tick_engine PRIVATE /W4)
else()
    target_compile_options(tick_engine PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Install targets
install(TARGETS tick_engine
    RUNTIME DESTINATION bin
)

# Enable testing
enable_testing()

# Test executable
add_executable(test_tick_engine tests/test_tick_engine.cpp src/tick_handler.cpp src/order_book.cpp)
target_link_libraries(test_tick_engine PRIVATE Threads::Threads ${HIREDIS_LIBRARY})

if(TARGET nlohmann_json::nlohmann_json)
    target_link_libraries(test_tick_engine PRIVATE nlohmann_json::nlohmann_json)
endif()

add_test(NAME TickEngineTests COMMAND test_tick_engine)

# CPack configuration
set(CPACK_GENERATOR "TGZ")
set(CPACK_PACKAGE_VERSION_MAJOR ${PROJECT_VERSION_MAJOR})
set(CPACK_PACKAGE_VERSION_MINOR ${PROJECT_VERSION_MINOR})
set(CPACK_PACKAGE_VERSION_PATCH ${PROJECT_VERSION_PATCH})
include(CPack)
