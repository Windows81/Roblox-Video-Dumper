#!/bin/sh
# shellcheck disable=SC2086
f=$(grep -F -l -r "VALUE=\"https://hls-segments.rbxcdn.com" "$LOCALAPPDATA/Temp/Roblox/http")
realpath $f | xargs -I "{}" -n 1 grep -o -P -a -m 1 "https://\C+" {}