#!/bin/bash
function foo() {
        echo "foo.aVar=$aVar"
        aVar=anyVal
}

function fooLocal() {
        local aVar
        echo "fooLocal.aVar=$aVar"
        aVar=anyVal
}

aVar=theInitVal
foo
echo "aVar=$aVar"

aVar=theInitVal
fooLocal
echo "aVar=$aVar"
