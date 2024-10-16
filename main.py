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


def parse_inner_m3u(data: bytes, base_url: str) -> bytes:
    paths = re.findall(
        rb'\s*(\S+\.webm)',
        data,
    )
    return b'\n'.join(
        b'file %s/%s' % (
            base_url.encode(),
            path,
        )
        for path in paths
    )


def get_concats(prefix: str, urls: list[str]) -> list[str]:
    paths = []

    for url in urls:
        path = f'{prefix}-{url.rsplit('-', 1)[-1]}.concat'
        base_url = url.rsplit('/', 1)[0]
        paths.append(path)

        with open(path, 'wb') as f:
            f.write(parse_inner_m3u(urllib3.request('GET', url).data, base_url))
    return paths


def download(hash: str, location: str):
    assert os.path.isdir(location)

    url = get_url(hash)
    data = urllib3.request('GET', url).data

    path_prefix = os.path.join(location, url[-32:])
    m3u8_urls = parse_top_m3u(data)
    concat_paths = get_concats(path_prefix, m3u8_urls)

    subprocess.Popen([
        'ffmpeg',
        *(
            arg
            for url in concat_paths
            for arg in [
                '-safe', '0',
                '-f', 'concat',
                '-protocol_whitelist',
                'https,tls,tcp,file,data',
                '-i', url,
            ]
        ),
        *(
            arg
            for i in range(len(m3u8_urls))
            for arg in [
                '-map', f'{i:d}',
            ]
        ),
        '-c', 'copy',
        '-reset_timestamps', '1',
        '-fflags', '+genpts',
        f'{path_prefix}.mp4',
        '-y',
    ]).communicate()
    print(m3u8_urls)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'hash', type=str, default='https://c1.rbxcdn.com/8bbd730825219577bac81de41e418c08', nargs='?',
    )
    parser.add_argument(
        'location', type=str, default='./videos/', nargs='?',
    )
    download(**parser.parse_args().__dict__)
