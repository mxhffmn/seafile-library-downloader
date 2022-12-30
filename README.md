# Seafile Library Downloader

This tool is designed to be used as a backup solution for a private Seafile library/repository on a NAS or some other
kind of storage device. The usage is simple and can be customized to a certain degree with parameters (see below). The
output are multiple ZIP files, i.e., one ZIP file for each directory within the Seafile library.

## Usage

A simple shell script such as the one below can be used to run the tool:

```
#!/bin/sh

pip install requests

# define variables here or as environment variables
#AUTH_TOKEN="Auth"
#REPO_ID="RepoID"
#SAVE_DIR="."
#SERVER="seafile.rlp.net"

python seafile.py --save_dir "$SAVE_DIR" --server "$SERVER" "$AUTH_TOKEN" "$REPO_ID"
```

Make sure to have Python3 installed on your system and also install the library _requests_. Afterwards, gather some
information that is needed to run the application:

* The authentication token is needed to authenticate at the Seafile Web API that delivers the data for downloading. You
  can find this token in your Seafile profile.
* The ID of the repository/library to download can be found in the URL that is shown when opening the library in your
  browser. It should look something like this: `https://[SEAFILE_SERVER]/library/[REPO_ID]/[REPO_NAME]/`

These two parameters are required when running the application. All other parameters are optional and change the
behavior of the tool:

* **server**: The server where the repository is located.
* **--save_dir**: The path to save the downloaded ZIP files to.
* **--sleep_time**: The time interval (in seconds) to wait between consecutive requests for asking if a ZIP file is
  ready to be downloaded.
* **--wait_time**: The total time to wait for a ZIP file to be created.
* **--remove_unknown**: If set, all ZIP files in the output directory that do not match directories in the
  Seafile library are removed after downloading is finished.

## Limitations

It is currently not possible to download directories that exceed a certain maximum size specified by the server. These
downloads will fail at some point while the application is running and a log message is printed. To avoid this issue, it
is possible to move some files into other top-level directories in the library. It is planned to work around this
limitation by automatically downloading and zipping child directories of these problematic directories which are finally
extracted again and combined to a single ZIP.
