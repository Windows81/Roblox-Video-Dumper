from io import BufferedReader
import save
import glob
import os
import re


def call_process(rbxcdn_hash: bytes, m3u8_urls: list[bytes]):
    save.download_and_combine(
        rbxcdn_hash.decode('utf-8'),
        [
            u.decode('utf-8')
            for u in m3u8_urls
        ],
        './videos/',
    )


def process_file(file: BufferedReader):
    hls_base: bytes
    rbxcdn_hash: bytes = b''
    m3u8_urls: list[bytes] = []

    rbxcdn_match = re.search(
        br'[0-9]\.rbxcdn\.com/([0-9a-f]+)',
        file.readline(),
    )
    if not rbxcdn_match:
        return
    rbxcdn_hash = rbxcdn_match.group(1)

    for i, line in enumerate(file):
        # b'NAME="RBX-BASE-URI"' is usually matched at i == 25.
        # There is no way that the M3U data is so many lines down.
        # Terminate early.
        if i > 40:
            return
        if b'NAME="RBX-BASE-URI"' not in line:
            continue
        hls_match = re.search(
            br'(https://hls-segments.rbxcdn.com/[0-9a-f]+)',
            line,
        )
        assert hls_match
        hls_base = hls_match.group(1)
        break
    else:
        return

    for line in file:
        if b'RBX-BASE-URI}/' in line:
            modified_line = re.sub(b'^.+RBX-BASE-URI}', hls_base, line)
            m3u8_urls.append(modified_line.strip())

    return rbxcdn_hash, m3u8_urls


def process_files(directory_path: str):
    for file_path in glob.glob(directory_path):
        with open(file_path, 'rb') as file:
            res = process_file(file)
            if res:
                yield res


if __name__ == "__main__":
    directory_path = os.path.expandvars("$LOCALAPPDATA/Temp/Roblox/http/*")
    for res in process_files(directory_path):
        call_process(*res)
