#!/usr/bin/env python3
# -*- coding:UTF-8 -*-
#
# Copyright (C) 2025 Junbo Zheng. All rights reserved.
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

import os
import gzip
import argparse


def unzip_gz_files_and_merge(directory, log_file, output_file):
    with open(output_file, "wb") as merged_file:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".gz"):
                    gz_file_path = os.path.join(root, file)

                    with gzip.open(gz_file_path, "rb") as f_in:
                        decompressed_data = f_in.read()

                    merged_file.write(decompressed_data)
                    print(f"file {gz_file_path} unzip and merge successfully......")

        if os.path.isfile(log_file):
            with open(log_file, "rb") as tmp_log:
                merged_file.write(tmp_log.read())
                print(f"file {log_file} has been merged...")

    print(f"Good job! All files has been merge to {output_file} ...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="both .gz file and the log file will be unzip and merge"
    )
    parser.add_argument(
        "--log_file",
        type=str,
        default="tmp.log",
        help="specify the log file to be merged, tmp.log is used by default",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="output.log",
        help="specify the name of the output file, output.log is used by default",
    )
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="specify the directory to search, current directory by default",
    )

    args = parser.parse_args()

    if not os.path.isfile(args.log_file):
        print(f"log file {args.log_file} not exist, ignore")

    unzip_gz_files_and_merge(args.path, args.log_file, args.output_file)
