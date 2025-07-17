package main

import (
	"strconv"
	"strings"
)

func parseFloat(s string) float64 {
	f, err := strconv.ParseFloat(s, 64)
	if err != nil {
		return 0
	}
	return f
}

func parseApps(s string) []uint32 {
	strs := strings.Split(s, ",")
	var apps []uint32
	for _, str := range strs {
		if id, err := strconv.Atoi(str); err == nil {
			apps = append(apps, uint32(id))
		}
	}
	return apps
}