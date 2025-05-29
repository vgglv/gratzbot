#pragma once
#include "types.hpp"

namespace gratzbot {
    class CommandExecutor {
    public:
        CommandExecutor();
        ~CommandExecutor();
        void processUpdate(const Update& u);
    private:
        std::vector<Command> commands;
    };
}