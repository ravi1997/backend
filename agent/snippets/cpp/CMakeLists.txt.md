# Snippet: Standard `CMakeLists.txt`

```cmake

cmake_minimum_required(VERSION 3.20)
project(MyApp VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable testing

include(CTest)
enable_testing()

# Build Type

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# Source files

add_executable(MyApp src/main.cpp)

# Libraries (Example)

# find_package(Threads REQUIRED)

# target_link_libraries(MyApp PRIVATE Threads::Threads)

# Testing

if(BUILD_TESTING)
  add_executable(MyAppTest tests/test_main.cpp)
  add_test(NAME MyAppTest COMMAND MyAppTest)
endif()

```
