#! /usr/bin/python3
# -*- coding:UTF-8 -*-
import shutil
import subprocess
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
        self.source_path = '~/Downloads'
        self.output_path = "./file"
        self.output_file = "file.tar.gz"
        self.merge_file = "./merged.log"
        self.filter_pattern = "log\\d*|tmp.log"
        self.tmp_log = "tmp.log"


default_cli_parameters = DefaultCLIParameters()


class ShellRunner:
    @staticmethod
    def command_run(command, password=None):
        run_cmd = command.split(" ")
        if password is not None and "sudo" in run_cmd:
            run_cmd.insert(0, "echo \"%s\"|" % password + "\n")
            run_cmd.insert(run_cmd.index("sudo") + 1, "-S")

        run_cmd = " ".join(run_cmd)
        return subprocess.run(run_cmd, stdin=sys.stdin, stdout=sys.stdout, shell=True).returncode


class CLIParametersParser:
    def __init__(self):
        print('Parameter Number :', len(sys.argv))
        print('Parameter Lists  :', str(sys.argv))
        print('Shell Name       :', str(sys.argv[0]))

        arg_parser = argparse.ArgumentParser(
            description=
            "Extract a file with the suffix `.tar.gz` from the source path or remote path and extract to output_path."
        )
        arg_parser.add_argument('-o', '--output_path',
                                type=str,
                                nargs='+',
                                default=default_cli_parameters.output_path,
                                help="extract packet output path")
        arg_parser.add_argument('-P', '--password',
                                type=str,
                                nargs='?',
                                default=default_cli_parameters.password,
                                help="extract packet and chmod with user password")
        arg_parser.add_argument('-s', '--source_path',
                                type=str,
                                nargs='+',
                                default=default_cli_parameters.source_path,
                                help="extract packet from source path",
                                required=True)
        arg_parser.add_argument('-m', '--merge_file',
                                type=str,
                                nargs='+',
                                default=default_cli_parameters.merge_file,
                                help="extract packet and merge to a new file")
        arg_parser.add_argument(
            '-f', '--filename',
            type=str,
            nargs=1,
            help=
            "extract packet filename, the default file suffix is .tar.gz, such as: log.tar.gz",
            required=True)
        arg_parser.add_argument(
            '-p', '--purge_source_file',
            help=
            'purge source file if is true',
            action='store_true',
            default=False)
        arg_parser.add_argument(
            '-F', '--filter_pattern',
            type=str,
            default=default_cli_parameters.filter_pattern,
            help='filter the files to be merged')

        self.__cli_args = arg_parser.parse_args()

        print(self.output_path)
        print(self.source_path)
        print(self.filename)
        print(self.purge_source_file)

    def __getattr__(self, item):
        return self.__cli_args.__getattribute__(item)

    def __set__(self, instance, value):
        self.__cli_args.__set__(instance, value)


def get_full_path(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == default_cli_parameters.tmp_log:
                return os.path.abspath(root)


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
    ShellRunner.command_run(cmd)


def pull_from_source_path(args):
    if args.source_path[0] == "phone":
        args.source_path[0] = default_cli_parameters.remote_path
        adb_cmd = "adb pull " + args.source_path[0] + " " + "./"
        print(adb_cmd)
        ShellRunner.command_run(adb_cmd)

        file = os.getcwd() + "/devicelog/**/" + "*" + args.filename[0] + "*.tar*.gz"
        result = glob.glob(file, recursive=True)
    else:
        pattern = args.source_path[0] + "/" + "*" + args.filename[0] + "*.tar*.gz"
        result = glob.glob(pattern)

    print("source path from %s, glob result %s" % (args.source_path[0], result))

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
    ShellRunner.command_run(cmd)

    cmd = "sudo chmod -R 755" + " " + args.output_path
    ShellRunner.command_run(cmd, args.password)


if __name__ == '__main__':
    # parse command line args
    cli_args = CLIParametersParser()

    if os.path.exists(cli_args.output_path):
        input_str = input("The %s already exists, will cover it? [Y/N]\n" %
                          cli_args.output_path)
        if input_str != 'Y':
            print("quit and exit")
            sys.exit(0)

    cmd = "sudo rm -rf " + cli_args.output_path
    print("%s path exist, remove, cmd %s" % (cli_args.output_path, cmd))
    ShellRunner.command_run(cmd, cli_args.password)

    file = pull_from_source_path(cli_args)
    if file is None:
        print("not found file packet")
        sys.exit()

    print("output file %s" % file)
    extract_and_chmod(cli_args, file)

    # file is temp, need to remove
    os.remove(file)

    path = get_full_path(cli_args.output_path)
    print("full path %s" % path)

    # gunzip all *.gz files under path
    gunzip_all(path)

    # remove unused .gz files
    remove_all_suffix_gz_file(path)

    # merge all file to a new file
    merge_logfiles(path, cli_args)

    # remove output_path since it has been merge to a new file
    cmd = "sudo rm -rf" + " " + cli_args.output_path
    ShellRunner.command_run(cmd, cli_args.password)
