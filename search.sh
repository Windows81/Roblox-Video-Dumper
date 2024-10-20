#!/bin/shrob
# shellcheck disable=SC2086
files=$(grep -F -l -r "VALUE=\"https://hls-segments.rbxcdn.com" "$LOCALAPPDATA/Temp/Roblox/http")
if [[ -n $files ]]; then
    realpath $files | xargs -I "{}" -n 1 grep -o -P -a -m 1 "https://\C+" {}
else
    echo "No files found."
fi