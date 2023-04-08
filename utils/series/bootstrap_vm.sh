#!/bin/bash
REMOTE_REPO_URL="https://github.com/black-ejs/rlgin"

cd ~
if [[ -d dev ]]
then
	echo "     ##### ~/dev already exists"
else
	mkdir -p ~/dev
fi

cd ~/dev

# force refresh whether or not it's already a good repo
if [[ -d rlgin ]]
then
	rm -rf rlgin
fi
git clone "${REMOTE_REPO_URL}"

mkdir -p ~/dev/projects/training_ground


