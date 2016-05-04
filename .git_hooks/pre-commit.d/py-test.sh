#!/bin/bash
if [ -d '.pytest-runner' ] ; then
  exec .pytest-runner
else
  exec py.test
fi
