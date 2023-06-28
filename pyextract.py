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
from enum import IntEnum


class DefaultCLIParameters:
    password = "123456"
    remote_path = "/sdcard/Android/data/com.mi.health/files/log/devicelog"
    source_path = "~/Downloads"
    output_path = "./file"
    output_file = "file.tar.gz"
    merge_file = "./merged.log"
    filter_pattern = "log\\d*|tmp.log"
    tmp_log = "tmp.log"


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
        print("Parameter Number :", len(sys.argv))
        print("Parameter Lists  :", str(sys.argv))
        print("Shell Name       :", str(sys.argv[0]))

        arg_parser = argparse.ArgumentParser(
            description="Extract a file with the suffix `.tar.gz` from the source path or remote path and extract to "
                        "output_path."
        )
        arg_parser.add_argument('-o', '--output_path',
                                type=str,
                                nargs='+',
                                default=DefaultCLIParameters.output_path,
                                help="extract packet output path")
        arg_parser.add_argument('-P', '--password',
                                type=str,
                                nargs='?',
                                default=DefaultCLIParameters.password,
                                help="extract packet and chmod with user password")
        arg_parser.add_argument('-s', '--source_path',
                                type=str,
                                nargs='+',
                                default=DefaultCLIParameters.source_path,
                                help="extract packet from source path",
                                required=True)
        arg_parser.add_argument('-m', '--merge_file',
                                type=str,
                                nargs='+',
                                default=DefaultCLIParameters.merge_file,
                                help="extract packet and merge to a new file")
        arg_parser.add_argument(
            '-f', '--filename',
            type=str,
            nargs=1,
            help="extract packet filename, the default file suffix is .tar.gz, such as: log.tar.gz",
            required=True)
        arg_parser.add_argument(
            '-p', '--purge_source_file',
            help="purge source file if is true",
            action='store_true',
            default=False)
        arg_parser.add_argument(
            '-F', '--filter_pattern',
            type=str,
            default=DefaultCLIParameters.filter_pattern,
            help="filter the files to be merged")

        self.__cli_args = arg_parser.parse_args()

        print("output_path      :", self.output_path)
        print("source_path      :", self.source_path)
        print("filename         :", self.filename)
        print("purge_source_file:", self.purge_source_file)

    def __getattr__(self, item):
        return self.__cli_args.__getattribute__(item)

    def __set__(self, instance, value):
        self.__cli_args.__set__(instance, value)


class LogTools:
    def __init__(self, cli_parser):
        self.__cli_parser = cli_parser
        self.log_packet_path = None
        self.log_dir_path = None

    def clear_output_dir(self, ask=True):
        if not os.path.exists(self.__cli_parser.output_path):
            return 0

        # if exists output path, clear
        if ask:
            input_str = input("The %s already exists, will cover it? [Y/N]\n" %
                              self.__cli_parser.output_path)
            if input_str != 'Y':
                print("quit and exit")
                return -1

        cmd = "sudo rm -rf " + self.__cli_parser.output_path
        print(Highlight.Convert("clear") + " exist file %s by command %s" % (self.__cli_parser.output_path, cmd))
        return ShellRunner.command_run(cmd, self.__cli_parser.password)

    def pull_packet(self):
        if self.__cli_parser.source_path[0] == "phone":
            self.__cli_parser.source_path[0] = DefaultCLIParameters.remote_path
            adb_cmd = "adb pull " + self.__cli_parser.source_path[0] + " " + "./"
            print(adb_cmd)
            ShellRunner.command_run(adb_cmd)

            file = os.getcwd() + "/devicelog/**/" + "*" + self.__cli_parser.filename[0] + "*.tar*.gz"
            result = glob.glob(file, recursive=True)
        else:
            pattern = self.__cli_parser.source_path[0] + "/" + "*" + self.__cli_parser.filename[0] + "*.tar*.gz"
            result = glob.glob(pattern)

        print(Highlight.Convert("pull") + " %s from %s" % (result, self.__cli_parser.source_path[0]))

        if len(result) == 0:
            return -1

        if len(result) > 1:
            index = input("Please input the file index you want to extract:\n")
            file = result[int(index)]
        else:
            file = result[0]

        path, unused = os.path.split(file)
        output = self.__cli_parser.filename[0] + "_" + DefaultCLIParameters.output_file
        output = os.path.join(path, output)

        if self.__cli_parser.purge_source_file:
            print("rename to %s" % output)
            os.rename(file, output)
        else:
            print("copy to %s" % output)
            shutil.copyfile(file, output)

        if output is None:
            print("not found file packet")
            return -1
        self.log_packet_path = output
        print("output file %s" % self.log_packet_path)

        return 0

    def __find_logfiles_path__(self):
        for root, dirs, files in os.walk(self.__cli_parser.output_path):
            for file in files:
                if file == DefaultCLIParameters.tmp_log:
                    self.log_dir_path = os.path.abspath(root)
                    return 0
        return -1

    def __remove_all_suffix_gz_file__(self):
        for root, dirs, files in os.walk(self.log_dir_path):
            for file in files:
                if os.path.splitext(file)[-1] == ".gz":
                    os.remove(os.path.join(root, file))
        return 0

    def __gunzip_all__(self):
        if not os.path.exists(self.log_dir_path):
            return -1

        dirs = os.listdir(self.log_dir_path)
        for file in dirs:
            if ".gz" in file:
                filename = file.replace(".gz", "")
                gzip_file = gzip.GzipFile(self.log_dir_path + '/' + file)
                with open(os.path.join(self.log_dir_path, filename), "wb+") as f:
                    f.write(gzip_file.read())
        print("\n" + Highlight.Convert("gunzip") + " all finish")
        return 0

    def extract_packet(self):
        if not os.path.exists(self.__cli_parser.output_path):
            os.makedirs(self.__cli_parser.output_path)

        cmd = "tar -xzvf " + self.log_packet_path + " -C " + self.__cli_parser.output_path
        print(Highlight.Convert("extract") + " by command " + cmd)
        if ShellRunner.command_run(cmd) != 0:
            return -1

        cmd = "sudo chmod -R 755" + " " + self.__cli_parser.output_path
        if ShellRunner.command_run(cmd, self.__cli_parser.password) != 0:
            return -1

        # file is temp, need to remove
        os.remove(self.log_packet_path)

        # find log files dir path
        if self.__find_logfiles_path__() != 0:
            return -1

        # gunzip all *.gz files under path
        if self.__gunzip_all__() != 0:
            return -1

        # remove unused .gz files
        return self.__remove_all_suffix_gz_file__()

    def merge_logfiles(self):
        # merge all file to a new file
        file_list = os.listdir(self.log_dir_path)
        file_list.sort()
        print(Highlight.Convert("merge") + " file list %s" % file_list)

        if os.path.exists(self.__cli_parser.merge_file):
            print("merge file exist, will remove")
            os.remove(self.__cli_parser.merge_file)

        cmd = "cat "
        for file in file_list:
            if re.match(self.__cli_parser.filter_pattern, file) is None:
                continue
            cmd += os.path.join(self.log_dir_path, file) + " "

        cmd += ">" + " " + self.__cli_parser.merge_file
        print("merge file by command %s" % cmd)
        return ShellRunner.command_run(cmd)


def CHECK_ERROR_EXIT(ret):
    if ret != 0:
        print(Highlight.Convert("failure", Highlight.RED))
        exit(ret)


class Highlight(IntEnum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    WHITE = 37

    @staticmethod
    def Convert(msg, color=BLUE):
        return "\033[;%dm%s\033[0m" % (color, msg)


if __name__ == '__main__':
    # parse command line args
    cli_args = CLIParametersParser()

    logtools = LogTools(cli_args)

    # clear exist output dir
    CHECK_ERROR_EXIT(logtools.clear_output_dir())

    # pull log packet from phone or local, depends on command line parameters
    CHECK_ERROR_EXIT(logtools.pull_packet())

    # extract log packet
    CHECK_ERROR_EXIT(logtools.extract_packet())

    # merge the log files to one file, then remove output dir
    if logtools.merge_logfiles() == 0:
        logtools.clear_output_dir(False)
    print(Highlight.Convert("Successful", Highlight.GREEN))
