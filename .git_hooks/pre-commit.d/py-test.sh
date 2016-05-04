#!/bin/bash
if [ -d '.pytest-runner' ] ; then
  . .pytest-runner
  echo $?
else
  py.test
  return $?
fi
