#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess as sp
import shutil


def copy_dir(source, target):
    #  print(f"copying {source} to {target}")
    shutil.copytree(source, target, dirs_exist_ok=True)
    #  sp.run(["cp", "-rf", source, target])


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

#      # database internal
    #  shutil.rmtree("./docs/db", ignore_errors=True)
    #  os.mkdir("./docs/db")
    #  copy_dir("./src/db_src/docs", "./docs/db")
    #  copy_dir("./style", "./docs/css")
    #  copy_dir("./style", "./docs/db/css")

    #  shutil.rmtree("./docs/tracing", ignore_errors=True)
    #  os.mkdir("./docs/tracing")
    #  copy_dir("./src/tracing/docs", "./docs/tracing")
    #  copy_dir("./style", "./docs/css")
    #  copy_dir("./style", "./docs/tracing/css")

    #  shutil.rmtree("./docs/https:", ignore_errors=True)
    #  shutil.rmtree("./src/https:", ignore_errors=True)


if __name__ == '__main__':
    run()

