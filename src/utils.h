#pragma once

// reads a contents of a file and returns a pointer
char* read_file(const char *filename);

// converts string to a enum CONDITION_* 
int condition_flag_from_string(const char *s);
