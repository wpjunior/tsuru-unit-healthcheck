#!/usr/bin/env python

import logging
import argparse
import os
import json
import sys

try:
    from urllib2 import Request, urlopen, HTTPError
except ImportError:
    from urllib.request import Request, urlopen, HTTPError


TSURU_TARGET = os.environ['TSURU_TARGET']
TSURU_TOKEN = os.environ['TSURU_TOKEN']


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    parser = argparse.ArgumentParser(
        description='Get healthcheck for all units'
    )
    parser.add_argument('-a', metavar='app', type=str,
                        help='Name of app')

    parser.add_argument('-p', metavar='path', type=str,
                        default='/healthcheck',
                        help='Path of healthcheck')

    args = parser.parse_args()
    get_units(args.a, args.p)


def get_units(app, path):
    url = '%s/apps/%s' % (TSURU_TARGET, app)
    req = Request(url, None, {'Authorization': TSURU_TOKEN})

    try:
        resp = urlopen(req, timeout=3)
    except Exception as err:
        logging.exception(err)
        return

    if resp.code != 200:
        logging.error('Failed to get unit list: %d', resp.code)
        return

    ok = True
    data = json.loads(resp.read().decode('utf-8'))

    for unit in data['units']:
        if unit['ProcessName'] != 'web':
            logging.warn('[%s] skip task: %s', unit['Ip'], unit['ProcessName'])
            continue

        if unit['Status'] != 'started':
            logging.warn('[%s] skip status: %s', unit['Ip'], unit['Status'])
            continue

        if not healthcheck_unit(unit, path):
            ok = False

    if not ok:
        sys.exit(1)


def healthcheck_unit(unit, path):
    addr = unit['Address']
    url = "%s://%s%s" % (addr['Scheme'], addr['Host'], path)

    try:
        resp = urlopen(url, timeout=5)
    except HTTPError as err:
        logging.error('[%s] Failed to healthcheck unit: %s', url, err)

        if hasattr(err, 'file'):
            logging.error(err.file.read().decode('utf-8'))
        else:
            logging.error(err.read())

        return False

    except Exception as err:
        logging.error('[%s] Failed to healthcheck unit: %s', url, err)
        return False

    if resp.code == 200:
        logging.info('[%s] Healthcheck OK', url)
    else:
        logging.error(
            '[%s] Failed to healthcheck unit, status code: %s, body: %s',
            url, str(resp.code), resp.read())
        return False

    return True


if __name__ == '__main__':
    main()
