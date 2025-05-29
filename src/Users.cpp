#include "Users.hpp"

namespace {
    gratzbot::Users users;
}

namespace gratzbot {
    Users* Users::instance() {
        return &users;
    }

    Users::Users() {

    }

    Users::~Users() {

    }
}