#pragma once
#include <vector>
#include <optional>

namespace gratzbot {
    struct Env {
        std::string key;
        std::string value;
    };

    class EnvContainer {
    public:
        void parseDotEnv();
        std::optional<std::string> getEnv(std::string_view key);
    private:
        std::vector<Env> variables;
    };

}
