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
import glob
import subprocess


def extract_tar_gz():
    current_dir = os.getcwd()
    tar_gz_files = glob.glob(os.path.join(current_dir, "*.tar.gz"))

    if not tar_gz_files:
        print("not found any .tar.gz files")
        return

    print(f"found {len(tar_gz_files)} .tar.gz files")

    for file_path in tar_gz_files:
        file_name = os.path.basename(file_path)
        print(f"extract: {file_name}")

        try:
            result = subprocess.run(
                ["tar", "-xzvf", file_path],
                cwd=current_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.stdout:
                print(result.stdout)
            print(f"✓ extract success: {file_name}")
        except subprocess.CalledProcessError as e:
            print(f"✗ extract failed: {file_name}")
            print(f"error message: {e.stderr}")
            print(f"return code: {e.returncode}")
            if "Permission denied" in e.stderr:
                print("hint: please use 'sudo' to run this script")


if __name__ == "__main__":
    extract_tar_gz()
