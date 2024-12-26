package main

import "errors"

func Index[T comparable](s []T, x T) (int, error) {
	for i, v := range s {
		if v == x {
			return i, nil
		}
	}
	return -1, errors.New("value not found")
}

func string_to_reaction_type(emoji string) []ReactionType {
	return []ReactionType{
		{"emoji", emoji},
	}
}
