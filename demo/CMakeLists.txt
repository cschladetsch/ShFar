cmake_minimum_required(VERSION 3.22)
project(FarTrainingDemo LANGUAGES CXX)

add_library(mylib_static
    src/Parser.cpp
    src/Widget.cpp
)

target_include_directories(mylib_static PUBLIC include)

