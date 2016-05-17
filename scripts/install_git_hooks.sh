#!/bin/bash

[ -d $PWD/.git/hooks ] && rm -r $PWD/.git/hooks
rm -f $PWD/.git/hooks
ln -s $PWD/.git_hooks $PWD/.git/hooks
