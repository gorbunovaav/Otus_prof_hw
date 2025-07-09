#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import gzip
import sys
import glob
import logging
import collections
from optparse import OptionParser
# brew install protobuf
# protoc  --python_out=. ./appsinstalled.proto
# pip install protobuf
import appsinstalled_pb2
# pip install python-memcached
import memcache
import concurrent.futures
import time
import random
import multiprocessing


NORMAL_ERR_RATE = 0.01
AppsInstalled = collections.namedtuple("AppsInstalled", ["dev_type", "dev_id", "lat", "lon", "apps"])

def process_file(fn, device_memc, dry_run):
    memc_clients = create_memc_clients(device_memc)

    processed = errors = 0
    logging.info('Processing %s' % fn)
    with gzip.open(fn) as fd:
        for line in fd:
            line = line.strip()
            if not line:
                continue
            appsinstalled = parse_appsinstalled(line)
            if not appsinstalled:
                errors += 1
                continue
            memc_client = memc_clients.get(appsinstalled.dev_type)
            if not memc_client:
                errors += 1
                logging.error("Unknown device type: %s" % appsinstalled.dev_type)
                continue
            ok = insert_appsinstalled(memc_client, appsinstalled, dry_run)
            if ok:
                processed += 1
            else:
                errors += 1
    return fn, processed, errors

def create_memc_clients(device_memc):
    clients = {}
    for dev_type, address in device_memc.items():
        clients[dev_type] = memcache.Client([address], socket_timeout=3)
    return clients

def dot_rename(path):
    head, fn = os.path.split(path)
    # atomic in most cases
    os.rename(path, os.path.join(head, "." + fn))


def insert_appsinstalled(memc_client, appsinstalled, dry_run=False, max_retries=3):
    ua = appsinstalled_pb2.UserApps()
    ua.lat = appsinstalled.lat
    ua.lon = appsinstalled.lon
    ua.apps.extend(appsinstalled.apps)
    key = "%s:%s" % (appsinstalled.dev_type, appsinstalled.dev_id)
    packed = ua.SerializeToString()

    for attempt in range(max_retries):
        try:
            if dry_run:
                logging.debug("%s - %s -> %s" % (memc_client.servers[0], key, str(ua).replace("\n", " ")))
                return True
            else:
                if memc_client.set(key, packed):
                    return True
                else:
                    logging.warning("Memcache set failed for key %s (attempt %d)" % (key, attempt + 1))
        except Exception as e:
            logging.warning("Memcache error on attempt %d for key %s: %s" % (attempt + 1, key, e))

        time.sleep(0.1 * (2 ** attempt) + random.random() * 0.1)

    logging.error("Failed to write to memcache after %d attempts for key %s" % (max_retries, key))
    return False


def parse_appsinstalled(line):
    line_parts = line.strip().split("\t")
    if len(line_parts) < 5:
        return
    dev_type, dev_id, lat, lon, raw_apps = line_parts
    if not dev_type or not dev_id:
        return
    try:
        apps = [int(a.strip()) for a in raw_apps.split(",")]
    except ValueError:
        apps = [int(a.strip()) for a in raw_apps.split(",") if a.isdigit()]
        logging.info("Not all user apps are digits: `%s`" % line)
    try:
        lat, lon = float(lat), float(lon)
    except ValueError:
        logging.info("Invalid geo coords: `%s`" % line)
    return AppsInstalled(dev_type, dev_id, lat, lon, apps)

def main(options):
    device_memc = {
        "idfa": options.idfa,
        "gaid": options.gaid,
        "adid": options.adid,
        "dvid": options.dvid,
    }

    files = sorted(glob.glob(options.pattern))  
    if not files:
        logging.info("No files matching pattern: %s", options.pattern)
        return

    args = [(fn, device_memc, options.dry) for fn in files]

    logging.info("Starting multiprocessing for %d files", len(files))
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.starmap(process_file, args)

    for fn, processed, errors in results:
        if not processed:
            logging.warning("No data processed in %s", fn)
        else:
            err_rate = float(errors) / processed
            if err_rate < NORMAL_ERR_RATE:
                logging.info("Acceptable error rate (%s). Successful load", err_rate)
            else:
                logging.error("High error rate (%s > %s). Failed load", err_rate, NORMAL_ERR_RATE)

        dot_rename(fn)

def prototest():
    sample = "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23\ngaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
    for line in sample.splitlines():
        dev_type, dev_id, lat, lon, raw_apps = line.strip().split("\t")
        apps = [int(a) for a in raw_apps.split(",") if a.isdigit()]
        lat, lon = float(lat), float(lon)
        ua = appsinstalled_pb2.UserApps()
        ua.lat = lat
        ua.lon = lon
        ua.apps.extend(apps)
        packed = ua.SerializeToString()
        unpacked = appsinstalled_pb2.UserApps()
        unpacked.ParseFromString(packed)
        assert ua == unpacked


if __name__ == '__main__':
    op = OptionParser()
    op.add_option("-t", "--test", action="store_true", default=False)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("--dry", action="store_true", default=False)
    op.add_option("--pattern", action="store", default="/data/appsinstalled/*.tsv.gz")
    op.add_option("--idfa", action="store", default="127.0.0.1:33013")
    op.add_option("--gaid", action="store", default="127.0.0.1:33014")
    op.add_option("--adid", action="store", default="127.0.0.1:33015")
    op.add_option("--dvid", action="store", default="127.0.0.1:33016")
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO if not opts.dry else logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    if opts.test:
        prototest()
        sys.exit(0)

    logging.info("Memc loader started with options: %s" % opts)
    try:
        main(opts)
    except Exception as e:
        logging.exception("Unexpected error: %s" % e)
        sys.exit(1)
