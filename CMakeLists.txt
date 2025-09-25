cmake_minimum_required(VERSION 3.18)
project(gratzbot C)

set(CMAKE_EXPORT_COMPILE_COMMANDS 1)

find_package(ZLIB REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(CURL REQUIRED)

file(GLOB_RECURSE SOURCES "src/*.c" "src/*.h")

add_executable(${PROJECT_NAME} ${SOURCES})

target_link_libraries(${PROJECT_NAME} PRIVATE 
	CURL::libcurl 
	OpenSSL::SSL 
	OpenSSL::Crypto 
	ZLIB::ZLIB
)

target_include_directories(${PROJECT_NAME} PUBLIC "${CMAKE_SOURCE_DIR}/src")

set_target_properties(${PROJECT_NAME} PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}
)
if(MSVC)
	target_compile_options(${PROJECT_NAME} PRIVATE /W4 /WX-)
else()
	target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic -Wno-unused-parameter)
endif()

if(APPLE)
	set(CMAKE_INSTALL_RPATH_USE_LINK_PATH ON)
	set_target_properties(${PROJECT_NAME} PROPERTIES
		INSTALL_RPATH "@loader_path;@executable_path;@rpath"
	)
endif()
