# Python Extract Files

Extract a file with the suffix `.tar.gz` from the local path or remote path and extract to output_path.

For example, a compressed package(named `123456_abc.tar.gz`) that stores the other compressed packages and files, as follows:

```Shell
.
└── log
    └── file
        ├── 1.gz
        ├── 2.gz
        ├── 3.gz
        ├── 4.gz
        └── tmp.log
```

Ths compressed package suffix name must be with `.tar.gz`.

Additionally, the files in the `.tar.gz` package are compressed packages with `.gz` as the suffix, and include a specific file, used to help us find the path where the `.gz` file located. We assume it is called `tmp.log`, which is free and you can modify it according to you want.


# Usage

```Python
➜  /Users/junbozheng/project/pyextract git:(master) ./pyextract.py --help
Parameter Number : 2
Parameter Lists  : ['./pyextract.py', '--help']
Shell Name       : ./pyextract.py
usage: pyextract.py [-h] [--output_path OUTPUT_PATH [OUTPUT_PATH ...]] [--password PASSWORD [PASSWORD ...]] [--source_path SOURCE_PATH [SOURCE_PATH ...]] --filename FILENAME [--keep_source_file]

Extract a file with the suffix `.tar.gz` from the local path or remote path and extract to output_path.

optional arguments:
  -h, --help            show this help message and exit
  --output_path OUTPUT_PATH [OUTPUT_PATH ...]
                        extract packet output path
  --password PASSWORD [PASSWORD ...]
                        extract packet and chmod with user password
  --source_path SOURCE_PATH [SOURCE_PATH ...]
                        extract packet source packet
  --filename FILENAME   extract packet filename, the default file suffix is .tar.gz, such as: log.tar.gz
  --keep_source_file    keep source file in local path, copy to a new file without remove it if is true
```

`--filename` option must be filled in, otherwise `pyextract` may not know the index information about the file name you want to extract.

Two methods supported to extract compressed files:

```Shell
+------------------------+---------------------+
+        Android         +   -----------+      |
+         Phone          +              |      |
+  /sdcard/Android/data  +              |      |
+------------------------+             \|/     |
                                               |
                                              \|/    with `pyextract`
                                               |----------------------> to local output path
                                              /|\                     (./file path by default)
+----------------------+               /|\     |
+       Ubuntu         +                |      |
+        20.04         +                |      |
+  /home/mi/downloads  +     -----------+      |
+----------------------+-----------------------+
```

- **Ubuntu 20.04 LTS** local path with the `filename` and the suffix is `.tar.gz`. In this case, you can type

    ```Python
    ./pyextract.py --password 1234 --filename 123456_abc --source_path /Users/junbozheng/test
    ```

    When we have already downloaded the file we want to extract in advance, we can quickly extract it through `pyextract`.

- **Android phone** path with the `filename` and the suffix is `.tar.gz`. In this case, you can type

    ```Python
    ./pyextract.py --password 1234 --filename 123456_abc --source_path phone
    ```

    `pyextract` will use `adb pull` command to pull files from the **remote_path** to local and extract.

    When some files are stored on phone, we can pull them and extract them quickly with `pyextract`. In advance, our computer already connected to our phone through USB or the other ways.


# License

[pyextract](https://github.com/Junbo-Zheng/pyextract) is licensed under the Apache license, check the [LICENSE](./LICENSE) file.
