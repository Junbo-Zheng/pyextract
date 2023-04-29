#! /usr/bin/python3
# -*- coding:UTF-8 -*-

import shutil
import sys
import os
import gzip
import glob

import argparse

password = "123456"
remote_path = "/sdcard/Android/data/com.mi.health/files/log/devicelog"
local_path = "Downloads"
output_path = "./file"
output_file = "file.tar.gz"

tmp_log = "tmp.log"


def get_full_path(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == tmp_log:
                return os.path.join(root, file)


def pull_from_source_path(args):
    if (args.source_path == "phone"):
        args.source_path = remote_path
        adb_cmd = "adb pull " + args.source_path + " " + "./"
        print(adb_cmd)
        os.system(adb_cmd)

        file = os.getcwd() + "/devicelog/**/" + args.filename[0] + "*.tar*.gz"
        result = glob.glob(file, recursive=True)
        print("glob result is %s" % result)
        result = glob.glob(file, recursive=True)
    else:
        path = os.path.join(
            os.environ['HOME'], "Downloads"
        ) if args.source_path == "Downloads" else args.source_path
        file = path + "/" + "*" + args.filename[0] + "*.tar*.gz"
        result = glob.glob(file)

    print("glob result %s" % result)

    if len(result) == 0:
        return None

    if len(result) > 1:
        index = input("Please input the file index you want to extract:\n")
        file = result[int(index)]
    else:
        file = result[0]

    path, unused = os.path.split(file)
    output = args.filename[0] + "_" + output_file
    output = os.path.join(path, output)

    if (args.keep_source_file):
        print("copy to %s" % output)
        shutil.copyfile(file, output)
    else:
        print("rename to %s" % output)
        os.rename(file, output)

    return output


def gunzip_all(path):
    if os.path.exists(path):
        dirs = os.listdir(path)
        for dir in dirs:
            if '.gz' in dir:
                filename = dir.replace(".gz", "")
                gzip_file = gzip.GzipFile(path + '/' + dir)
                with open(path + "/" + filename, 'wb+') as f:
                    f.write(gzip_file.read())
    print("gunzip all finish")


def extract_and_chmod(args, file):
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    cmd = "tar -xzvf " + file + " -C " + args.output_path
    os.system('echo %s | sudo -S %s' % (args.password[0], cmd))

    cmd = "sudo chmod -R 777" + " " + args.output_path
    os.system('echo %s | sudo -S %s' % (args.password[0], cmd))


if __name__ == '__main__':
    print('Parameter Number :', len(sys.argv))
    print('Parameter Lists  :', str(sys.argv))
    print('Shell Name       :', str(sys.argv[0]))

    arg_parse = argparse.ArgumentParser(
        description=
        "Extract a file with the suffix `.tar.gz` from the local path or remote path and extract to output_path."
    )
    arg_parse.add_argument('--output_path',
                           type=str,
                           nargs='+',
                           default=output_path,
                           help="extract packet output path")
    arg_parse.add_argument('--password',
                           type=str,
                           nargs='+',
                           default=password,
                           help="extract packet and chmod with user password")
    arg_parse.add_argument('--source_path',
                           type=str,
                           nargs='+',
                           default=local_path,
                           help="extract packet source packet")
    arg_parse.add_argument(
        '--filename',
        type=str,
        nargs=1,
        help=
        "extract packet filename, the default file suffix is .tar.gz, such as: log.tar.gz",
        required=True)
    arg_parse.add_argument(
        '--keep_source_file',
        help=
        'keep source file in local path, copy to a new file without remove it if is true',
        action='store_true',
        default=False)

    args = arg_parse.parse_args()

    print(args.output_path)
    print(args.source_path)
    print(args.filename)
    print(args.keep_source_file)

    if os.path.exists(args.output_path):
        input_str = input("The %s already exists, will cover it? [Y/N]\n" %
                          args.output_path)
        if input_str != 'Y':
            print("quit and exit")
            sys.exit(0)

        cmd = "rm -rf " + args.output_path
        print("%s path exist, remove, cmd %s" % (args.output_path, cmd))
        os.system('echo %s | sudo -S %s' % (args.password[0], cmd))

    file = pull_from_source_path(args)
    if file is None:
        print("not found file packet")
        sys.exit()

    print("output file %s" % file)
    extract_and_chmod(args, file)

    # file is temp, need to remove
    os.remove(file)

    full = get_full_path(args.output_path)
    path, unused = os.path.split(full)
    print("full %s path %s, unused %s" % (full, path, unused))

    # gunzip all *.gz files under path
    gunzip_all(path)
