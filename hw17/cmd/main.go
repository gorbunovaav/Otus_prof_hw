package main

import (
	"bufio"
	"compress/gzip"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
)

type FileResult struct {
	Filename  string
	Processed int
	Errors    int
}

func processFile(fn string) FileResult {
	file, err := os.Open(fn)
	if err != nil {
		log.Println("Cannot open:", fn, err)
		return FileResult{Filename: fn, Errors: 1}
	}
	defer file.Close()

	gz, err := gzip.NewReader(file)
	if err != nil {
		log.Println("Gzip read error:", err)
		return FileResult{Filename: fn, Errors: 1}
	}
	defer gz.Close()

	scanner := bufio.NewScanner(gz)
	processed, errors := 0, 0

	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		ok := handleLine(line)
		if ok {
			processed++
		} else {
			errors++
		}
	}
	return FileResult{Filename: fn, Processed: processed, Errors: errors}
}

func dotRename(filename string) {
	dir := filepath.Dir(filename)
	base := filepath.Base(filename)
	newName := filepath.Join(dir, "."+base)
	err := os.Rename(filename, newName)
	if err != nil {
		log.Println("Rename failed:", err)
	}
}

func main() {
	pattern := "/path/to/*.tsv.gz" // <-- замени путь
	files, err := filepath.Glob(pattern)
	if err != nil {
		log.Fatal("Glob error:", err)
	}
	sort.Strings(files)

	results := make([]FileResult, len(files))
	var wg sync.WaitGroup
	resultChan := make(chan FileResult, len(files))

	for _, file := range files {
		wg.Add(1)
		go func(fn string) {
			defer wg.Done()
			resultChan <- processFile(fn)
		}(file)
	}

	wg.Wait()
	close(resultChan)

	i := 0
	for res := range resultChan {
		results[i] = res
		i++
	}

	sort.Slice(results, func(i, j int) bool {
		return results[i].Filename < results[j].Filename
	})

	for _, res := range results {
		errRate := float64(res.Errors) / float64(res.Processed)
		if errRate < 0.01 {
			log.Printf("OK (%s): %d processed, %d errors", res.Filename, res.Processed, res.Errors)
		} else {
			log.Printf("FAIL (%s): %d processed, %d errors", res.Filename, res.Processed, res.Errors)
		}
		dotRename(res.Filename)
	}
}
