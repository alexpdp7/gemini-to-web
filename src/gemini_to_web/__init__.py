import argparse
import pathlib
import shutil

import htmlgenerator

from gemini_to_web import html

def converter():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=pathlib.Path)
    parser.add_argument("target", type=pathlib.Path)
    args = parser.parse_args()

    shutil.copytree(args.source, args.target)
    for gmi in args.target.glob("**/*.gmi"):
        html_path = gmi.with_suffix(".html")
        html_path.write_text(
            html.pretty(
                htmlgenerator.render(
                    html.to_html(gmi.read_text()),
                    {}
                )
            )
        )
