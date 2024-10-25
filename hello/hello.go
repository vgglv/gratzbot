package main

import (
	"fmt"
	"github.com/vgglv/gratzbot/greetings"
)

func main() {
	message := greetings.Hello("Baska")
	fmt.Println(message)
}
