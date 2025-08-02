#!/bin/bash
#
##https://stackoverflow.com/questions/35741323/how-to-find-if-remote-host-is-reachable-over-ssh-without-actually-doing-ssh
#if (exec 3<>/dev/tcp/api.dler.io/25500) 2> /dev/null; then
#    echo open
#else
#    echo closed
#fi

# Add the -f option to curl if server errors like HTTP 404 should fail too


#https://unix.stackexchange.com/questions/190163/shell-command-script-to-see-if-a-host-is-alive
TARGET=https://api.dler.io
if [ curl -I "$TARGET" > /dev/null 2>&1 ]; then
  echo "$TARGET alive and web site is up"
else
  echo "$TARGET offline or web server problem"
fi