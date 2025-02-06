package main

import (
	"errors"
	"strings"
)

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

func contains_exact_word(t1 string, t2 string) bool {
	lowercase_text := strings.ToLower(t1)
	words := strings.Fields(lowercase_text)

	for _, word := range words {
		if word == t2 {
			return true
		}
	}
	return false
}
