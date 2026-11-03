#!/bin/bash

###############################################################################
############################### MainMenu ######################################
###############################################################################
# https://askubuntu.com/questions/446156/pause-execution-and-wait-for-user-input
function MainMenu () {
    echo "Pressing \"YESIDO\" will delete all the files found as listed above."
    echo "Pressing \"NO\" to abort the program."
    read -p "Input Selection:" MainMenuInput
    local -r NO="NO"
    local -r YESIDO="YESIDO"
    if [ "${MainMenuInput,,}" = "${YESIDO,,}" ]; then
        return 0
    elif [ "${MainMenuInput,,}" = "${NO,,}" ]; then
        return 1
    else
        MainMenu
    fi
}

# This builds the main menu and routs the user to the function selected.

if ! MainMenu; then
    echo nononono
    exit 0
fi

echo yesyesyes

# This executes the main menu function.
# Let the fun begin!!!! WOOT WOOT!!!!

###############################################################################
################################### END #######################################
###############################################################################
