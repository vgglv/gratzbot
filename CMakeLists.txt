cmake_minimum_required(VERSION 3.18)
project(gratzbot C)

set(CMAKE_EXPORT_COMPILE_COMMANDS 1)

find_package(ZLIB REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(CURL REQUIRED)

file(GLOB_RECURSE SOURCES "src/*.c" "src/*.h")

add_executable(gratzbot ${SOURCES})

target_link_libraries(gratzbot PRIVATE CURL::libcurl OpenSSL::SSL OpenSSL::Crypto ZLIB::ZLIB)

target_include_directories(gratzbot PUBLIC "${CMAKE_SOURCE_DIR}/src")

if(MSVC)
	target_compile_options(gratzbot PRIVATE /W4 /WX-)
else()
	target_compile_options(gratzbot PRIVATE -Wall -Wextra -Wpedantic -Wno-unused-parameter)
endif()

if(APPLE)
	set(CMAKE_INSTALL_RPATH_USE_LINK_PATH ON)
	set_target_properties(gratzbot PROPERTIES
		INSTALL_RPATH "@loader_path;@executable_path;@rpath"
	)
endif()
