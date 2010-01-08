#!/bin/sh

# Test the hgcodesmell extension.

HG="hg --config extensions.codesmell=`pwd`/hgcodesmell.py"
msg() { echo "[ test ] $1"; }
die() { echo "[failed] $1"; exit 1; }
suc() { echo "[passed] $1"; exit 0; }

msg "Removing old test repository, if present."
rm -rf repo

msg "Making test repository in ./repo."
$HG init repo || die "repo creation failed"
cd repo

msg "Committing some files without smell."
echo "# A normal Python file." > file.py
echo "A text file." > file.txt
$HG addremove
$HG commit -vm "Initial commit." || die "initial commit failed"

msg "Trying to commit file.py with smell. codesmell should complain."
echo "1/0" >> file.py
echo | $HG commit -vm "Trying to commit file with smell."
[ $? -eq 1 ] || die "codesmell didn't exit with error"
$HG revert -a || die "revert failed"

msg "Trying to commit file.txt without smell. codesmell should not complain."
echo "1/0" >> file.txt
$HG commit -vm "Blah, blah." || die "commit failed"

msg "Removing test repository."
cd ..
rm -r repo

suc "all tests successful"