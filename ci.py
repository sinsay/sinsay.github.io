#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess as sp


def copy_dir(source, target):
    #  print(f"copying {source} to {target}")
    sp.run(["cp", "-r", source, target])


def walk_dir(r):
    for root, dirs, files in os.walk(r):
        for d in dirs:
            source = os.path.join(root, d)

            if not d.endswith("assets"):
                walk_dir(source)
                continue

            target = "./docs/"
            copy_dir(source, target)


def run():
    build = sp.run(["mdbook", "build", "-d", "docs"])

    if build.returncode != 0:
        print("Call mdboo failed")
        return

    walk_dir("./src/")
    copy_dir("./src/redis/image", "./docs/image")


if __name__ == '__main__':
    run()
