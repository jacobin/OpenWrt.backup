#!/bin/bash




# https://www.google.com/search?q=sed+escape+url+in+variable&pws=0&gl=us&gws_rd=cr
#     When using sed with a variable that might contain a URL, special characters within the URL can interfere with sed's syntax, especially if the URL contains the delimiter used in the sed command (e.g., / in s/old/new/).
#
#     There are two primary methods to handle this: Change the sed delimiter.
#
#     *Instead of using the default / as a delimiter, choose a character that is unlikely to appear in the URL, such as |, #, or @.
#         URL="http://example.com/path/to/resource?param=value&id=123"
#         # Using '|' as a delimiter
#         echo "This is a placeholder for a URL." | sed "s|placeholder|$URL|"
#
#
#     *Escape special characters in the URL variable:
#
#     If changing the delimiter is not feasible or desired, you can escape the special characters within the URL variable before passing it to sed. This typically involves escaping characters that have special meaning in regular expressions or sed commands, such as /, &, `\`, . (if used in the search pattern), and potentially others like ?, *, +, [, ], (, ), |, ^, $.
#         URL="http://example.com/path/to/resource?param=value&id=123"
#         # Escape '/' for use with '/' delimiter in sed
#         ESCAPED_URL=$(echo "$URL" | sed 's/\//\\&/g') # Escapes '/' to '\/'
#         echo "This is a placeholder for a URL." | sed "s/placeholder/$ESCAPED_URL/"
#
#     Note: When escaping characters, be mindful of the context (search pattern vs. replacement string) and the specific characters that need escaping. For replacement strings, & needs to be escaped as \& to prevent sed from interpreting it as the matched pattern. If the URL is in the search pattern, a more comprehensive escaping of regex metacharacters might be necessary.



URL="http://www.google.com:25500/abc.yaml"
ESCAPED_URL=$(echo "$URL" | sed 's/\//\\&/g') # Escapes '/' to '\/'

echo ${ESCAPED_URL}

sed -i -e "s|abc|$URL|g" ./file.txt
