#!/bin/sh

pip install requests

# define variables here or as environment variables
#AUTH_TOKEN="Auth"
#REPO_ID="RepoID"
#SAVE_DIR="."
#SERVER="seafile.rlp.net"

python seafile.py --save_dir "$SAVE_DIR" --server "$SERVER" "$AUTH_TOKEN" "$REPO_ID"
