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

func stringToReactionTypeSlice(emoji string) []ReactionType {
	return []ReactionType{
		{"emoji", emoji},
	}
}

func containsExactWord(t1 string, t2 string) bool {
	return strings.Contains(strings.ToLower(t1), t2)
}
