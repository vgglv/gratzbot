#pragma once

namespace gratzbot {
    class Users {
    public:
        Users();
        ~Users();

        static Users* instance();
    };
}