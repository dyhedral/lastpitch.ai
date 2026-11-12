#!/usr/bin/env python3
"""Check every HTML file has exactly one <h1>; optionally cap visible words.

Usage: check_html.py [--max-words N --words-file FILE]
Standard library only. Text inside script, style and svg is ignored.
"""
import argparse
import pathlib
import sys
from html.parser import HTMLParser

SKIP = {"script", "style", "svg"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.words = 0
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == "h1":
            self.h1 += 1
        if tag in SKIP:
            self.skip_depth += 1

    def handle_startendtag(self, tag, attrs):
        if tag == "h1":
            self.h1 += 1

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth:
            self.words += len(data.split())


def scan(path):
    p = Scan()
    p.feed(path.read_text(encoding="utf-8"))
    p.close()
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-words", type=int)
    ap.add_argument("--words-file", default="index.html")
    args = ap.parse_args()
    failed = False
    for path in sorted(pathlib.Path(".").rglob("*.html")):
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue
        s = scan(path)
        if s.h1 != 1:
            print(f"FAIL {path}: expected exactly one h1, found {s.h1}")
            failed = True
        else:
            print(f"ok   {path}: one h1")
        if args.max_words is not None and str(path) == args.words_file:
            if s.words >= args.max_words:
                print(f"FAIL {path}: {s.words} visible words, limit is under {args.max_words}")
                failed = True
            else:
                print(f"ok   {path}: {s.words} visible words (< {args.max_words})")
    return 1 if failed else 0


sys.exit(main())
