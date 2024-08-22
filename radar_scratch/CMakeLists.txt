cmake_minimum_required(VERSION 3.10)

# Project name and version
project(IWR VERSION 1.0)

# Specify the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Add the include directory
include_directories(include)

# Find the required package
find_package(PkgConfig REQUIRED)
pkg_check_modules(UDEV REQUIRED libudev)

# Fetch Json parser library for C++ using FetchContent
include(FetchContent)
FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG        v3.11.3  # Specify the version you want to use
)
FetchContent_MakeAvailable(nlohmann_json)

# Add the source files
set(SOURCES
    src/iwr_boot.cpp
    src/json/json.hpp
    src/json/json_functions.cpp
    src/cfg/adv_cams.json
)

# Define the executable target
add_executable(IWR ${SOURCES})

# Add adv_cams json file
file(COPY src/cfg/adv_cams.json
DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

# Link the libudev library
target_link_libraries(IWR ${UDEV_LIBRARIES})

# Include directories for libudev
target_include_directories(IWR PRIVATE ${UDEV_INCLUDE_DIRS})

# Include directories for nlohmann/json
target_include_directories(IWR PRIVATE ${nlohmann_json_SOURCE_DIR}/include)