#!/usr/bin/env bash

#set -x # echo on
SUDO=sudo
if [ "$GITHUB_ACTOR" == "nektos/act" ]; then
    echo "Running in 'act' container, not using sudo"
    SUDO=""

    # workaround for act nodeos-based container
    # see https://github.com/nektos/act/issues/251
    if [ ! -f "/etc/lsb-release" ]; then
        echo "Manually creating lsb-release file"
        echo "DISTRIB_RELEASE=18.04" > /etc/lsb-release
    fi
fi

if [ -n "$GITHUB_EVENT_PATH" ]; then
    echo "Printing action event JSON file:"
    cat $GITHUB_EVENT_PATH;
else
    echo "GITHUB_EVENT_PATH is not set!";
fi

echo "Dumping environment:"
printenv

echo "Updating apt sources:"
$SUDO apt update

echo "Installing packages:"
$SUDO apt install -y \
    tree \
    libc6 \
    git

echo "Dumping working tree structure:"
tree -Dphug
