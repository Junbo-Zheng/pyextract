#! /usr/bin/env python3
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


def unzip_gz_files_and_merge(directory, log_file, output_file):
    with open(output_file, "wb") as merged_file:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".gz"):
                    gz_file_path = os.path.join(root, file)
                    new_file_path = os.path.join(root, file[:-3])

                    with gzip.open(gz_file_path, "rb") as f_in:
                        decompressed_data = f_in.read()

                    merged_file.write(decompressed_data)
                    print(f"文件 {gz_file_path} 解压并合并成功...")

        with open(log_file, "rb") as tmp_log:
            merged_file.write(tmp_log.read())
            print(f"文件 {log_file} 的内容已添加到合并文件中...")

    print(f"所有文件已解压并合并到 {output_file} 中...")


if __name__ == "__main__":
    target_directory = "."
    tmp_log_file = "tmp.log"
    merged_file = "output.log"

    unzip_gz_files_and_merge(target_directory, tmp_log_file, merged_file)