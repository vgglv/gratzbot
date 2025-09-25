#pragma once
#include "types.h"
#include <stdbool.h>

bool Commands_Parse(CommandsArray* cmd_arr);
void Commands_Delete(CommandsArray* command);
