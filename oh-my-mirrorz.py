#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: expandtab ts=4 sts=4 sw=4

import subprocess
import requests
import sys
import os
import argparse

VERSION = '20220705'
CURL_VERSION = ''
UA_URL = 'https://mirrors.quickso.cn'

big = {
    'centos': '/7/isos/x86_64/CentOS-7-x86_64-Everything-2009.iso',
    'centos-vault': '/6.0/isos/x86_64/CentOS-6.0-x86_64-LiveDVD.iso',
    'opensuse': '/distribution/leap/15.4/iso/openSUSE-Leap-15.4-DVD-x86_64-Media.iso',
    'ubuntu-releases': '/20.04/ubuntu-20.04.3-desktop-amd64.iso',
    'debian-cd': '/current/amd64/iso-bd/debian-edu-11.2.0-amd64-BD-1.iso',
    'kali-images': '/kali-2021.4/kali-linux-2021.4-live-amd64.iso',
    'CTAN': '/systems/texlive/Images/texlive2021-20210325.iso',
    'blackarch': '/iso/blackarch-linux-full-2021.09.01-x86_64.iso',
    'archlinux': '/iso/2022.02.01/archlinux-2022.02.01-x86_64.iso',
    'ubuntu': '/indices/md5sums.gz',
    'debian': '/ls-lR.gz',
}

# filled by CI
mirrors = ["https://mirrors.quickso.cn/static/json/legacy/tuna.json","https://mirrors.quickso.cn/static/json/legacy/opentuna.json","https://mirrors.quickso.cn/static/json/legacy/bfsu.json","https://mirrors.quickso.cn/static/json/legacy/bjtu.json","https://mirrors.quickso.cn/static/json/legacy/njupt.json","https://mirrors.quickso.cn/static/json/legacy/cqu.json","https://mirrors.quickso.cn/static/json/legacy/hit.json","https://mirrors.quickso.cn/static/json/legacy/nju.json","https://mirrors.quickso.cn/static/json/legacy/hust.json","https://mirrors.quickso.cn/static/json/legacy/neusoft.json","https://mirrors.quickso.cn/static/json/legacy/lzu.json","https://mirrors.quickso.cn/static/json/legacy/pku.json","https://mirrors.quickso.cn/static/json/legacy/byrio.json","https://mirrors.quickso.cn/static/json/legacy/cqupt.json","https://mirrors.quickso.cn/static/json/legacy/ynuosa.json","https://mirrors.quickso.cn/static/json/legacy/xjtu.json","https://mirrors.quickso.cn/static/json/legacy/xtom.json","https://mirrors.quickso.cn/static/json/legacy/xtom-hk.json","https://mirrors.quickso.cn/static/json/legacy/xtom-de.json","https://mirrors.quickso.cn/static/json/legacy/xtom-nl.json","https://mirrors.quickso.cn/static/json/legacy/xtom-ee.json","https://mirrors.quickso.cn/static/json/legacy/xtom-jp.json","https://mirrors.quickso.cn/static/json/legacy/xtom-au.json","https://mirrors.quickso.cn/static/json/legacy/wsyu.json","https://mirrors.quickso.cn/static/json/legacy/bupt.json","https://mirrors.quickso.cn/static/json/legacy/njtech.json","https://mirrors.quickso.cn/static/json/legacy/geekpie.json","https://cors.quickso.cn/?https://mirrors.ustc.edu.cn/static/json/mirrorz.json","https://mirror.sjtu.edu.cn/mirrorz/siyuan.json","https://mirrors.sjtug.sjtu.edu.cn/mirrorz/zhiyuan.json","https://mirrors.dgut.edu.cn/static/mirrorz.json","https://mirrors.sustech.edu.cn/mirrorz/mirrorz.json","https://cors.quickso.cn/?https://mirrors.nwafu.edu.cn/api/mirrorz/info.json","https://cors.quickso.cn/?https://mirror.iscas.ac.cn/.mirrorz/mirrorz.json","https://cors.quickso.cn/?https://linux.xidian.edu.cn/mirrors/status.json","https://mirrors.zju.edu.cn/api/mirrorz.json","https://mirrors.sdu.edu.cn/mirrorz.json","https://cors.quickso.cn/?https://mirrors.scau.edu.cn/mirrorz.d.json","https://cors.quickso.cn/?https://mirror.nyist.edu.cn/mirrorz.json","https://uestclug.github.io/mirrors-status/mirrorz.d.json"]

map = {}
res = {}

def check_curl():
    global CURL_VERSION
    try:
        res = subprocess.run(['curl', '--version'], stdout=subprocess.PIPE)
        out = res.stdout.decode('utf-8')
        CURL_VERSION = out.split()[1]
        print(out)
        return 0
    except:
        print("No curl found!")
        return -1

def site_info(url):
    return requests.get(url,
                        headers={
                            'User-Agent': 'oh-my-mirrorz/%s (+https://github.com/mirrorz-org/oh-my-mirrorz) %s %s' % (VERSION, UA_URL, requests.utils.default_user_agent())
                        }, timeout=10).json()


def speed_test(url, args):
    opt = '-qs'
    if args.ipv4:
        opt += '4'
    elif args.ipv6:
        opt += '6'
    res = subprocess.run(['curl', opt, '-o', os.devnull, '-w', '%{http_code} %{speed_download}',
                          '-m'+str(args.time), '-A', 'oh-my-mirrorz/%s (+https://github.com/mirrorz-org/oh-my-mirrorz) %s curl/%s' % (VERSION, UA_URL, CURL_VERSION), url], stdout=subprocess.PIPE)
    code, speed = res.stdout.decode('utf-8').split()
    return int(code), float(speed)

def human_readable_speed(speed):
    scale = ['B/s', 'KiB/s', 'MiB/s', 'GiB/s', 'TiB/s']
    i = 0
    while (speed > 1024.0):
        i += 1
        speed /= 1024.0
    return f'{speed:.2f} {scale[i]}'

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-4", "--ipv4", help="IPv4 only when speed testing", action="store_true")
    group.add_argument("-6", "--ipv6", help="IPv6 only when speed testing", action="store_true")
    parser.add_argument("-t", "--time", type=int, default=5, choices=[3, 5, 10, 30, 60], help="Duration of a speed test for one mirror (default: %(default)d)")
    args = parser.parse_args()

    if check_curl() != 0:
        exit(-1)
    for url in mirrors:
        try:
            map[url] = site_info(url)
            print('Loaded', map[url]['site']['abbr'], ':', map[url]['site']['url'])
        except:
            print('! Failed to load', url)
            pass

    print() # one empty line to separate metadata and speedtest

    for _, v in map.items():
        uri_list = []
        if 'big' in v['site']:
            uri_list.append(v['site']['big'])
        for r, u in big.items():
            for m in v['mirrors']:
                if m['cname'] == r:
                    uri_list.append(m['url'] + u)
        if len(uri_list) == 0:
            print('! No big file found for', v['site']['abbr'], v['site']['url'])
            continue

        for uri in uri_list:
            res[v['site']['abbr']] = 0
            print('Speed testing', v['site']['abbr'], uri if uri.startswith("http") else v['site']['url'] + uri, '... ', end='', flush=True)
            code, speed = speed_test(v['site']['url'] + uri, args)
            if code != 200:
                print('HTTP Code', code, 'Speed', human_readable_speed(speed))
            else:
                print(human_readable_speed(speed))
                res[v['site']['abbr']] = speed
                break

    print() # one empty line to separate speedtest and result

    print('RANK', 'ABBR', 'SPEED', sep='\t\t')
    for i, (k, v) in enumerate(sorted(res.items(), key = lambda x: x[1], reverse=True)):
        print(f'{i:02d}:', k, human_readable_speed(v), sep='\t\t')

if __name__ == '__main__':
    main()
