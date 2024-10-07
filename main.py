import subprocess
import argparse
import urllib3
import os.path
import re


def get_url(hash: str) -> str:
    # https://devforum.roblox.com/t/roblox-cdn-how-do-i-know-which-one-to-use/1274498/2
    if 'rbxcdn' in hash:
        return hash
    i = 31
    hash32 = hash[:32]
    for char in hash32:
        i ^= ord(char)  # i ^= int(char, 16) also works
    return f"https://c{i % 8}.rbxcdn.com/{hash32}"


def parse_top_m3u(data: bytes) -> list[str]:
    # FFmpeg doesn't support attributes such as `EXT-X-DEFINE`.
    # I'm writing this function myself for that reason.
    match = re.search(
        rb'#EXT-X-DEFINE:NAME="RBX-BASE-URI",VALUE="([^"]+)',
        data,
    )
    assert match is not None
    base_uri = match[1]
    urls = re.findall(
        rb'\{\$RBX-BASE-URI\}(/[^\s]+)',
        data,
    )
    return [
        (b'%s%s' % (base_uri, item)).decode()
        for item in urls
    ]


def download(hash: str, location: str):
    url = get_url(hash)
    data = urllib3.request('GET', url).data
    urls = parse_top_m3u(data)
    if os.path.isdir(location):
        location = os.path.join(location, f'{url[-32:]}.mp4')
    subprocess.Popen([
        'ffmpeg',
        *(
            arg
            for url in urls
            for arg in ['-i', url]
        ),
        *(
            arg
            for i in range(len(urls))
            for arg in ['-map', f'{i:d}']
        ),
        '-c', 'copy',
        location,
        '-y',
    ]).communicate()
    print(urls)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'hash', type=str, default='https://c1.rbxcdn.com/8bbd730825219577bac81de41e418c08', nargs='?',
    )
    parser.add_argument(
        'location', type=str, default='.', nargs='?',
    )
    download(**parser.parse_args().__dict__)
