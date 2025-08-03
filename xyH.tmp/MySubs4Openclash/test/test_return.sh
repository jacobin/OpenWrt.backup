#!/bin/bash

#https://www.linuxjournal.com/content/return-values-bash-functions#:~:text=When
#https://stackoverflow.com/questions/17336915/return-value-in-a-bash-function

###############################################################################
function func() {
    return 3
}

###############################################################################
function func2() {
    return
}

###############################################################################
func
res=$?
echo $res

###############################################################################
func2
res=$?
echo $res

###############################################################################
func
if [ $? -ne 0 ]; then
    echo func not equa 0
else
    echo func equa 0
fi

###############################################################################
func2
if [ $? -ne 0 ]; then
    echo func2 not equa 0
else
    echo func2 equa 0
fi

###############################################################################
source "./test_return_sub.sh"
if [ $? -ne 0 ]; then
    echo test_return_sub.sh not equa 0
else
    echo test_return_sub.sh equa 0
fi

###############################################################################
source "./test_return_sub2.sh"
if [ $? -ne 0 ]; then
    echo test_return_sub2.sh not equa 0
else
    echo test_return_sub2.sh equa 0
fi

###############################################################################
source "./test_return_sub3.sh"
if [ $? -ne 0 ]; then
    echo test_return_sub3.sh not equa 0
else
    echo test_return_sub3.sh equa 0
fi