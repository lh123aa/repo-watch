#!/usr/bin/env python3
# repo-watch setup helper: generate the Startup VBS for auto-start.
# Reads inputs from environment variables set by setup.bat (avoids cmd
# quote-mangling of Chinese paths in argv):
#   RW_ROOT   - project root (directory containing repo_watch.py)
#   RW_SCRIPT - full path to repo_watch.py
# Falls back to argv[1], argv[2] if env vars are absent.
# Writes: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\repo-watch.vbs
import os, sys


def main():
    root = os.environ.get("RW_ROOT", "")
    script = os.environ.get("RW_SCRIPT", "")
    if not root or not script:
        if len(sys.argv) >= 3:
            root = root or sys.argv[1]
            script = script or sys.argv[2]
    if not root or not script:
        print("usage: set RW_ROOT=... RW_SCRIPT=... python _gen_vbs.py")
        sys.exit(2)

    root = root.rstrip("\\")
    startup = os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
    )
    vbs_path = os.path.join(startup, "repo-watch.vbs")
    lines = [
        'Set WshShell = CreateObject("WScript.Shell")',
        'WshShell.CurrentDirectory = "%s"' % root,
        'WshShell.Run "pythonw ""%s"", 0, False' % script,
        'WScript.Quit',
    ]
    content = "\r\n".join(lines) + "\r\n"
    os.makedirs(startup, exist_ok=True)
    with open(vbs_path, "w", encoding="gbk") as f:
        f.write(content)
    print("written:", vbs_path)


if __name__ == "__main__":
    main()