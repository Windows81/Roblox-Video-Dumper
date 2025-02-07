#!/bin/sh
awk -b '''
BEGIN { n = 1 }
match($0, /[0-9]\.rbxcdn\.com\/([0-9a-f]+)/, v) { hash = v[1] }
/NAME="RBX-BASE-URI"/ { match($0, "(https://hls-segments.rbxcdn.com/[0-9a-f]+)", a); if (n) { n = 0 } else { print "" } printf hash }
/RBX-BASE-URI}/ { sub(/^.+RBX-BASE-URI}/, a[1], $0); printf " " $0 }
''' "$LOCALAPPDATA/Temp/Roblox/http"/* | xargs --max-lines=1 python ./main.py