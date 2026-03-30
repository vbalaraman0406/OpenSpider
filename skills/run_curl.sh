#!/bin/bash
curl -s -L -H 'User-Agent: Mozilla/5.0' 'https://trends24.in/united-states/' 2>/dev/null | head -c 5000
