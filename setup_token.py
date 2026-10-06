#!/usr/bin/env python3
# repo-watch setup helper: write repo_watch.config.json from env vars.
# set by setup.bat:
#   RW_CONFIG - full path to repo_watch.config.json
#   RW_TOKEN  - the GitHub token to write
import json, os, pathlib, sys


def main():
    cfg = os.environ.get("RW_CONFIG", "")
    tok = os.environ.get("RW_TOKEN", "")
    if not cfg or not tok:
        if len(sys.argv) >= 3:
            cfg = cfg or sys.argv[1]
            tok = tok or sys.argv[2]
    if not cfg or not tok:
        print("usage: set RW_CONFIG=... RW_TOKEN=... python setup_token.py")
        sys.exit(2)

    p = pathlib.Path(cfg)
    data = {"github_token": tok}
    # ??????? (??????)
    if p.exists():
        try:
            old = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(old, dict):
                old.update(data)
                data = old
        except Exception:
            pass
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("written:", cfg)


if __name__ == "__main__":
    main()