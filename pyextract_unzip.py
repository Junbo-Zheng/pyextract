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

import glob
import zipfile

def main():
    # Get all zip files in the current directory
    zip_files = glob.glob('*.zip')

    if not zip_files:
        print("No zip files found")
        return

    print("Found zip files. Extracting...")

    for zip_file in zip_files:
        print(f"Extracting: {zip_file}")
        try:
            # Open the zip file in read mode and extract all contents
            with zipfile.ZipFile(zip_file, 'r') as zf:
                zf.extractall()  # Extract to current directory (overwrites existing files)
        except zipfile.BadZipFile:
            print(f"  Error: {zip_file} is not a valid ZIP file")
        except PermissionError:
            print(f"  Error: Permission denied for {zip_file}")
        except Exception as e:
            print(f"  Extraction failed: {str(e)}")

    print("Extraction complete!")

if __name__ == "__main__":
    main()
