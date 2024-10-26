package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
)

var stocksDB []Stock

// reads into current []Stock slice from stocks.json
func Stocks_loadDB() error {
	content, err := os.ReadFile("stocks.json")
	if err != nil {
		return err
	}
	err = json.Unmarshal(content, &stocksDB)
	if err != nil {
		return err
	}
	fmt.Println(stocksDB)
	return nil
}

// saves current []Stock slice to a stocks.json file
func Stocks_saveDB() error {
	json, err := json.Marshal(stocksDB)
	if err != nil {
		return err
	}
	err = os.WriteFile("stocks.json", json, 0644)
	if err != nil {
		return err
	}
	return nil
}

// saves current []Stock slice to a stocks.json.bak file
func Stocks_saveBackupDB() error {
	json, err := json.Marshal(stocksDB)
	if err != nil {
		return err
	}
	err = os.WriteFile("stocks.json.bak", json, 0644)
	if err != nil {
		return err
	}
	return nil
}

func Stocks_getStock(name string) (*Stock, error) {
	for _, v := range stocksDB {
		if v.Name == name {
			return &v, nil
		}
	}
	return nil, errors.New("StocksDB: value not found")
}

func Stocks_setStock(s Stock) error {
	if len(s.Name) == 0 {
		return errors.New("Stock: could not be empty")
	}
	if s.Stocks_available <= 0 {
		return errors.New("Stock: stocks available can't be negative or 0")
	}
	var foundIndex int = -1
	for i, v := range stocksDB {
		if v.Name == s.Name {
			foundIndex = i
			break
		}
	}
	if foundIndex > -1 {
		fmt.Printf("Setting stock, was: %v, becomes: %v\n", stocksDB[foundIndex], s)
		stocksDB[foundIndex] = s
		return nil
	}
	stocksDB = append(stocksDB, s)
	fmt.Printf("Appending stock: %v\n", s)

	return nil
}

func Stocks_calculateCurrentPriceForStock(stock_name string) (float32, error) {
	var price float32 = 0
	return price, nil
}
