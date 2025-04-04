#! /usr/bin/env python3
# -*- coding:UTF-8 -*-
#
# Copyright (C) 2023 Junbo Zheng. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
    filter_pattern = "log\\d*|tmp.log"
    tmp_log = "tmp.log"
    special_file_prefix = ["core-", "minidump"]


class ShellRunner:
    @staticmethod
    def command_run(command, password=None):
        run_cmd = command.split(" ")
        if password is not None and "sudo" in run_cmd:
            run_cmd.insert(0, 'echo "%s"|' % password + "\n")
            run_cmd.insert(run_cmd.index("sudo") + 1, "-S")

        run_cmd = " ".join(run_cmd)
        return subprocess.run(
            run_cmd, stdin=sys.stdin, stdout=sys.stdout, shell=True
        ).returncode


class CLIParametersParser:
    def __init__(self):
        print("Parameter Number :", len(sys.argv))
        print("Shell Name       :", str(sys.argv[0]))

        arg_parser = argparse.ArgumentParser(
            description="Extract a file with the suffix `.tar.gz` from the source path or remote path and extract to "
            "output_path."
        )
        arg_parser.add_argument(
            "-o",
            "--output_path",
            type=str,
            nargs="+",
            default=DefaultCLIParameters.output_path,
            help="extract packet output path",
        )
        arg_parser.add_argument(
            "-P",
            "--password",
            type=str,
            nargs="?",
            default=DefaultCLIParameters.password,
            help="extract packet and chmod with user password",
        )
        arg_parser.add_argument(
            "-s",
            "--source_path",
            type=str,
            nargs="+",
            default=DefaultCLIParameters.source_path,
            help="extract packet from source path",
            required=True,
        )
        arg_parser.add_argument(
            "-m",
            "--merge_file",
            type=str,
            nargs="?",
            help="extract packet and merge to a new file",
        )
        arg_parser.add_argument(
            "-f",
            "--filename",
            type=str,
            nargs=1,
            help="extract packet filename, the default file suffix is .tar.gz, such as: log.tar.gz",
            required=True,
        )
        arg_parser.add_argument(
            "-p",
            "--purge_source_file",
            help="purge source file if is true",
            action="store_true",
            default=False,
        )
        arg_parser.add_argument(
            "-F",
            "--filter_pattern",
            type=str,
            default=DefaultCLIParameters.filter_pattern,
            help="filter the files to be merged",
        )

        self.__cli_args = arg_parser.parse_args()

        # extract the filename without suffix
        pattern = r"^(.*?)\.tar.*\.gz$"
        match = re.match(pattern, self.filename[0])
        if match:
            self.filename[0] = match.group(1)

        # With the input filename parameter as merge file if merge file is not specified
        if self.merge_file is None:
            self.merge_file = os.path.join(os.getcwd(), self.filename[0] + ".log")

        print("output_path      :", self.output_path)
        print("source_path      :", self.source_path)
        print("filename         :", self.filename)
        print("purge_source_file:", self.purge_source_file)
        print("merge_file       :", self.merge_file)

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

        # if output path exists, clear
        if ask:
            input_str = input(
                "The %s already exists, will cover it? [Y/N]\n"
                % self.__cli_parser.output_path
            )
            if input_str != "Y":
                print("quit and exit")
                return -1

        cmd = "sudo rm -rf " + self.__cli_parser.output_path
        print(
            Highlight.Convert("clear")
            + " exist file %s by command %s" % (self.__cli_parser.output_path, cmd)
        )
        return ShellRunner.command_run(cmd, self.__cli_parser.password)

    def pull_packet(self):
        if self.__cli_parser.source_path[0] == "phone":
            self.__cli_parser.source_path[0] = DefaultCLIParameters.remote_path
            adb_cmd = "adb pull " + self.__cli_parser.source_path[0] + " " + "./"
            print(adb_cmd)
            ShellRunner.command_run(adb_cmd)

            file = (
                os.getcwd()
                + "/devicelog/**/"
                + "*"
                + self.__cli_parser.filename[0]
                + "*.tar*.gz"
            )
            result = glob.glob(file, recursive=True)
        else:
            pattern = (
                self.__cli_parser.source_path[0]
                + "/"
                + "*"
                + self.__cli_parser.filename[0]
                + "*.tar*.gz"
            )
            result = glob.glob(pattern)

        if len(result) == 0:
            return -1

        print(
            Highlight.Convert("pull")
            + " %s from %s" % (result, self.__cli_parser.source_path[0])
        )

        if len(result) > 1:
            index = input("Please input the file index you want to extract:\n")
            file = result[int(index)]
        else:
            file = result[0]

        path = os.path.dirname(file)
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

    def __find_special_files(self):
        special_files = []
        for root, dirs, files in os.walk(self.log_dir_path):
            for file in files:
                # Check if the file starts with any prefix in special_file_prefix
                for prefix in DefaultCLIParameters.special_file_prefix:
                    if file.lower().startswith(prefix.lower()):
                        special_files.append(os.path.join(root, file))
        return special_files

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
                gzip_file = gzip.GzipFile(self.log_dir_path + "/" + file)
                with open(os.path.join(self.log_dir_path, filename), "wb+") as f:
                    f.write(gzip_file.read())
        print("\n" + Highlight.Convert("gunzip") + " all finish")
        return 0

    def extract_special_files(self):
        special_files = self.__find_special_files()
        if not special_files:
            print("No special files found")
            return 0

        print("Special files found:")
        for special_file in special_files:
            print("  ->", special_file)
            des_path = os.path.join(os.getcwd(), os.path.basename(special_file))
            copy_cmd = f"cp {special_file} {des_path}"
            print(f"Copying {special_file} to {des_path}")
            os.system(copy_cmd)

        return 0

    def extract_packet(self):
        if not os.path.exists(self.__cli_parser.output_path):
            os.makedirs(self.__cli_parser.output_path)

        cmd = "gzip -d " + self.log_packet_path
        print(Highlight.Convert("gzip") + " by command " + cmd)
        ShellRunner.command_run(cmd)

        tar_package = self.log_packet_path.replace(".gz", "")
        cmd = "tar -xvf " + tar_package + " -C " + self.__cli_parser.output_path
        print(Highlight.Convert("tar") + " by command " + cmd)
        if ShellRunner.command_run(cmd) != 0:
            return -1

        cmd = "sudo chmod -R 755" + " " + self.__cli_parser.output_path
        if ShellRunner.command_run(cmd, self.__cli_parser.password) != 0:
            return -1

        # tar_package is tmp file, since it's has replaced from .tar.gz to .tar, let's remove it
        os.remove(tar_package)

        # find log files dir path
        if self.__find_logfiles_path__() != 0:
            return -1

        # gunzip all *.gz files under path
        if self.__gunzip_all__() != 0:
            return -1

        # remove unused .gz files
        return self.__remove_all_suffix_gz_file__()

    # merge all file to a new file
    def merge_logfiles(self):
        file_list = os.listdir(self.log_dir_path)
        file_list.sort(key=lambda name: (len(name), name))
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


if __name__ == "__main__":
    # parse command line args
    cli_args = CLIParametersParser()

    logtools = LogTools(cli_args)

    # clear exist output dir
    CHECK_ERROR_EXIT(logtools.clear_output_dir())

    # pull log packet from phone or local, depends on command line parameters
    CHECK_ERROR_EXIT(logtools.pull_packet())

    # extract log packet
    CHECK_ERROR_EXIT(logtools.extract_packet())

    # extract special file
    CHECK_ERROR_EXIT(logtools.extract_special_files())

    # merge the log files to one file, then remove output dir
    if logtools.merge_logfiles() == 0:
        logtools.clear_output_dir(False)

    print(Highlight.Convert("Successful", Highlight.GREEN))
