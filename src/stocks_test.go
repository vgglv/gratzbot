package main

import (
	"testing"
)

func Test_checkStock(t *testing.T) {
	stocksDB = append(stocksDB, Stock{
		Name:  "Microsoft",
		Stocks_available: 100,
	})

	microsoftStock, err := Stocks_getStock("Microsoft")
	if err != nil {
		t.Fatal("Couldn't find a stock of microsoft: ", err)
	}

	expected_name := "Microsoft"
	expected_stocks_available := 100
	if microsoftStock.Name != expected_name {
		t.Errorf("Expected equality of %v = %v", microsoftStock.Name, expected_name)
	}
	if microsoftStock.Stocks_available != expected_stocks_available {
		t.Errorf("Expected equality of %v = %v", microsoftStock.Stocks_available, expected_stocks_available)
	}
}

func Test_stockManipulation(t *testing.T) {
	stocksDB = append(stocksDB, Stock{
		Name:  "Microsoft",
		Stocks_available: 100,
	})

	microsoftStock, err := Stocks_getStock("Microsoft")
	if err != nil {
		t.Fatal("Couldn't find a stock of microsoft: ", err)
	}
	microsoftStock.Stocks_available -= 10
	err = Stocks_setStock(*microsoftStock)
	if err != nil {
		t.Fatal("Couldn't set stock of microsoft: ", err)
	}

	checkStock, err := Stocks_getStock("Microsoft")

	if microsoftStock.Stocks_available != checkStock.Stocks_available {
		t.Errorf("Expected equality of %v = %v", microsoftStock.Stocks_available, checkStock.Stocks_available)
	}
}
