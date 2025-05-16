from . import save
import glob
import os
import re

hls_base: bytes = b''
rbxcdn_hash: bytes = b''
m3u8_urls: list[bytes] = []


def call_process():
    global hls_base, rbxcdn_hash, m3u8_urls
    if rbxcdn_hash == b'':
        return
    if len(m3u8_urls) == 0:
        return

    save.download(
        rbxcdn_hash.decode('utf-8'),
        [
            u.decode('utf-8')
            for u in m3u8_urls
        ],
        './videos/',
    )
    del rbxcdn_hash
    m3u8_urls.clear()


def process_line(line: bytes):
    global hls_base, rbxcdn_hash, m3u8_urls

    match = re.search(br'[0-9]\.rbxcdn\.com/([0-9a-f]+)', line)
    if match:
        call_process()
        rbxcdn_hash = match.group(1)
        return

    if b'NAME="RBX-BASE-URI"' in line:
        match = re.search(
            b'(https://hls-segments.rbxcdn.com/[0-9a-f]+)', line)
        assert match
        hls_base = match.group(1)
        return

    if re.search(b'RBX-BASE-URI}/', line):
        if rbxcdn_hash and hls_base:
            modified_line = re.sub(b'^.+RBX-BASE-URI}', hls_base, line)
            m3u8_urls.append(modified_line.strip())


def process_files(directory_path: str):
    for file_path in glob.glob(directory_path):
        with open(file_path, 'rb') as file:
            for line in file:
                process_line(line)


directory_path = os.path.expandvars("$LOCALAPPDATA/Temp/Roblox/http/*")
process_files(directory_path)
call_process()
