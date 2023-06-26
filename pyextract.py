#! /usr/bin/python3
# -*- coding:UTF-8 -*-

import shutil
import sys
import os
import gzip
import glob
import re

import argparse


class DefaultCLIParameters:
    def __init__(self):
        self.password = "123456"
        self.remote_path = "/sdcard/Android/data/com.mi.health/files/log/devicelog"
        self.local_path = 'Downloads'
        self.output_path = "./file"
        self.output_file = "file.tar.gz"
        self.merge_file = "./merged.log"
        self.filter_pattern = "log\\d*|tmp.log"
        self.tmp_log = "tmp.log"


default_cli_parameters = DefaultCLIParameters()


def get_full_path(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == default_cli_parameters.tmp_log:
                return os.path.join(root, file)


def remove_all_suffix_gz_file(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[-1] == ".gz":
                os.remove(os.path.join(root, file))


def merge_logfiles(path, args):
    file_list = os.listdir(path)
    file_list.sort()
    print("prepare to paste file list %s" % file_list)

    if os.path.exists(args.merge_file):
        print("file exit and remove")
        os.remove(args.merge_file)

    cmd = "cat "
    for file in file_list:
        if re.match(args.filter_pattern, file) is None:
            continue
        cmd += os.path.join(path, file) + " "

    cmd += ">" + " " + args.merge_file
    print("cmd %s" % cmd)
    os.system(cmd)


def pull_from_source_path(args):
    if args.source_path[0] == "phone":
        args.source_path = default_cli_parameters.remote_path
        adb_cmd = "adb pull " + args.source_path + " " + "./"
        print(adb_cmd)
        os.system(adb_cmd)

        file = os.getcwd() + "/devicelog/**/" + "*" + args.filename[0] + "*.tar*.gz"
        result = glob.glob(file, recursive=True)
        print("glob result is %s" % result)
        result = glob.glob(file, recursive=True)
    else:
        root_path = os.path.join(
            os.environ['HOME'], "Downloads"
        ) if args.source_path[0] == "Downloads" else args.source_path[0]
        pattern = root_path + "/" + "*" + args.filename[0] + "*.tar*.gz"
        result = glob.glob(pattern)

    print("glob result %s" % result)

    if len(result) == 0:
        return None

    if len(result) > 1:
        index = input("Please input the file index you want to extract:\n")
        file = result[int(index)]
    else:
        file = result[0]

    path, unused = os.path.split(file)
    output = args.filename[0] + "_" + default_cli_parameters.output_file
    output = os.path.join(path, output)

    if args.purge_source_file:
        print("rename to %s" % output)
        os.rename(file, output)
    else:
        print("copy to %s" % output)
        shutil.copyfile(file, output)

    return output


def gunzip_all(path):
    if os.path.exists(path):
        dirs = os.listdir(path)
        for file in dirs:
            if '.gz' in file:
                filename = file.replace(".gz", "")
                gzip_file = gzip.GzipFile(path + '/' + file)
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
    arg_parse.add_argument('-o', '--output_path',
                           type=str,
                           nargs='+',
                           default=default_cli_parameters.output_path,
                           help="extract packet output path")
    arg_parse.add_argument('-P', '--password',
                           type=str,
                           nargs='+',
                           default=default_cli_parameters.password,
                           help="extract packet and chmod with user password")
    arg_parse.add_argument('-i', '--source_path',
                           type=str,
                           nargs='+',
                           default=default_cli_parameters.local_path,
                           help="extract packet source packet")
    arg_parse.add_argument('-O', '--merge_file',
                           type=str,
                           nargs='+',
                           default=default_cli_parameters.merge_file,
                           help="extract packet and merge to a new file")
    arg_parse.add_argument(
        '-f', '--filename',
        type=str,
        nargs=1,
        help=
        "extract packet filename, the default file suffix is .tar.gz, such as: log.tar.gz",
        required=True)
    arg_parse.add_argument(
        '-p', '--purge_source_file',
        help=
        'purge source file if is true',
        action='store_true',
        default=False)
    arg_parse.add_argument(
        '-F', '--filter_pattern',
        type=str,
        default=default_cli_parameters.filter_pattern,
        help='filter the files to be merged')

    args = arg_parse.parse_args()

    print(args.output_path)
    print(args.source_path)
    print(args.filename)
    print(args.purge_source_file)

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

    # remove unused .gz files
    remove_all_suffix_gz_file(path)

    # merge all file to a new file
    merge_logfiles(path, args)
