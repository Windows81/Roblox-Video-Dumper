#!/bin/sh
ls $(grep -F -l -r "VALUE=\"https://hls-segments.rbxcdn.com" "$LOCALAPPDATA/Temp/Roblox/http") -l