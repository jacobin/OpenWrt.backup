#!/bin/bash

function assert()
{
    E_PARAM_ERR=98
    E_ASSERT_FAILED=99

    if [ -z "$2" ];then
      return $E_PARAM_ERR
    fi

    lineno=$2

    if [ ! $1 ];then
      echo "File \"$0\", line $lineno, Assertion failed: \"$1\""
      exit $E_ASSERT_FAILED
    fi
}
## Example:
#    a=5
#    b=4
#    condition="$a -lt $b"
#
#    assert "$condition" $LINENO
#    #以下的代码只有当"assert"成功时才会继续执行
#
#    echo "This statement echoes only if the \"assert\" does not fail."
