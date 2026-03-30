#!/bin/bash
curl -s 'https://f1-dot-vish-cloud.wl.r.appspot.com/f1/assets/index-HfHv82_q.js' | grep -o '/f1/api\|/api\|baseURL\|race/schedule\|/races/' | sort | uniq -c | sort -rn
