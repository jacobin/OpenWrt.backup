#!/bin/bash

# https://stackoverflow.com/questions/15783701/which-characters-need-to-be-escaped-when-using-bash
echo 'I'\''m a s@fe $tring which ends in newline
'

# sed -e "s/'/'\\\\''/g; 1s/^/'/; \$s/\$/'/"
echo "s/'/'\\\\''/g"
echo "1s/^/'/"
echo "\$s/\$/'/"
echo "s/'/'\\\\''/g; 1s/^/'/; \$s/\$/'/"
