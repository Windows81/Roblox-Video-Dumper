You'll need Python to run the program and FFmpeg in your `$PATH` to process videos.

To perform on your machine, run [this Bash script](./perform.sh).

The important thing here is that it uses a specific `awk` routine to format the arguments. Make your own PowerShell script which does something simular.

```
usage: main.py [-h] [--location [LOCATION]] hash m3u8_urls [m3u8_urls ...]
```
