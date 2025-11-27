#!/bin/bash

#    # Main script logic or other commands
#    echo "Starting script..."
#
#    # Call the function defined later
#    my_function "Hello" "World"
#
#    echo "Script finished."
#
#    # Function definition at the end of the script
#    my_function() {
#      echo "Inside my_function:"
#      echo "Argument 1: $1"
#      echo "Argument 2: $2"
#    }



source <(sed '1,/^# HELPER FUNCTIONS #$/d' "$0")
fun ABC

exit





# HELPER FUNCTIONS #

fun () {
  echo "$@"
}