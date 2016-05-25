#!/bin/bash
if [ -d '.tox-runner' ] ; then
  . .tox-runner
  echo $?
else
  tox
  return $?
fi
