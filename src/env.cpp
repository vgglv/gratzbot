#include "env.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>

namespace gratzbot {
    void EnvContainer::parseDotEnv() {
        std::ifstream file{".env"};
        if (!file.is_open()) {
            std::cerr << "Error parsing .env file!\n";
            return;
        }
        auto trim = [](const std::string& s) -> std::string {
            auto start = s.find_first_not_of(" \t\r\n");
            auto end = s.find_last_not_of(" \t\r\n");
            return start == std::string::npos ? std::string{} : s.substr(start, end-start+1);
        };
        std::string line;
        while(std::getline(file, line)) {
            line = trim(line);
            if (line.empty()) {
                continue;
            }
            auto equal_pos = line.find('=');
            if (equal_pos == std::string::npos) {
                continue;
            }
            std::string key = trim(line.substr(0, equal_pos));
            std::string value = trim(line.substr(equal_pos + 1));

            if (key.empty()) {
                std::cerr << "While parsing file found an empty key!\n";
                continue;
            }
            if (value.empty()) {
                std::cerr << "While parsing file found an empty value! Key was: " << key << "\n";
                continue;
            }
            variables.emplace_back(Env{key, value});
        }
    }

    std::optional<std::string> EnvContainer::getEnv(std::string_view key) {
        auto it = std::ranges::find_if(variables, [key](const Env& e) {
            return key == e.key;
        });
        if (it != variables.end()) {
            return it->value;
        }
        return std::nullopt;
    }
}
