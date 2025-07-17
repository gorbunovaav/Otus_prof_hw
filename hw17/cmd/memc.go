package main

import (
	"fmt"
	"log"
	"strings"

	"github.com/bradfitz/gomemcache/memcache"
	"google.golang.org/protobuf/proto"

	pb "go_memc_loader/appsinstalled"
)

var deviceMemc = map[string]string{
	"idfa": "127.0.0.1:33013",
	"gaid": "127.0.0.1:33014",
	"adid": "127.0.0.1:33015",
	"dvid": "127.0.0.1:33016",
}

func handleLine(line string) bool {
	parts := strings.Split(line, "\t")
	if len(parts) < 5 {
		return false
	}
	devType, devID := parts[0], parts[1]
	lat, lon := parseFloat(parts[2]), parseFloat(parts[3])
	apps := parseApps(parts[4])

	if devType == "" || devID == "" || len(apps) == 0 {
		return false
	}

	ua := &pb.UserApps{
		Lat:  lat,
		Lon:  lon,
		Apps: apps,
	}
	key := fmt.Sprintf("%s:%s", devType, devID)
	data, err := proto.Marshal(ua)
	if err != nil {
		log.Println("Protobuf error:", err)
		return false
	}
	addr := deviceMemc[devType]
	if addr == "" {
		log.Println("Unknown device:", devType)
		return false
	}
	client := memcache.New(addr)
	err = client.Set(&memcache.Item{Key: key, Value: data})
	if err != nil {
		log.Println("Memcached error:", err)
		return false
	}
	return true
}