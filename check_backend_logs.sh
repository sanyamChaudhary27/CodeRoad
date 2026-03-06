#!/bin/bash
# Check backend logs on EC2

export PATH="/c/Program Files/Git/usr/bin:$PATH"

echo "Checking backend logs..."
ssh -i ~/.ssh/coderoad-key.pem ubuntu@100.48.103.123 "sudo journalctl -u coderoad -n 50 --no-pager"
