#pragma once
#include "types.h"
#include <stdbool.h>

bool Commands_Parse(CommandsArray* cmd_arr);
void command_delete(CommandsArray command);
