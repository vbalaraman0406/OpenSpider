#!/bin/bash
if [ -f 'workspace/trump_last_seen.txt' ]; then
  echo 'File exists'
else
  echo 'New post text' > workspace/trump_last_seen.txt
fi