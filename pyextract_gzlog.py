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


def unzip_gz_files(directory):

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".gz"):
                gz_file_path = os.path.join(root, file)
                new_file_path = os.path.join(root, file[:-3])
                with gzip.open(gz_file_path, "rb") as f_in:
                    with open(new_file_path, "wb") as f_out:
                        f_out.write(f_in.read())
                print(f"文件 {gz_file_path} 解压成功...")


if __name__ == "__main__":
    target_directory = "."
    unzip_gz_files(target_directory)
    print("所有.gz文件已全部解压完成...")
