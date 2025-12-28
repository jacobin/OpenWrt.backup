#!/bin/bash

base64="1578863387-956-H4sIAAAAAAAAA+1V227bMAzNs7+CcFHEARLnsjTpCvilW7A+tcOaPQ1DoDi0LcCWNIlOm3795FtzQdL1pRg2lDCgkDo8h7Qoh9DQveIr1L7atN7GBtYm43G5WjtcR5PxtDW8GI6G0+GH6XjYGgxHo8m0BYM3qmfPckNMA7S0lPQS7k/7/6idQUKkzFW//5TkTKRM+E8JT3I/lFlf9S/Gk+nl5eV47PBMSU2g8VduR8Y0firjmIvYibTMYGnGUMevkeXEozy9l7lynDP4JEXE41wjUIJNGpAEBhFP0akj/pIZHlZgr9gQLMOgPfg46cWcknzpV8taicFg6tusdhdSXGMaNAyfZ9ffv3QhkjpjFLTPPWZC4hl2DPTg3CvBBWvtZ2gMi63X7tgyoXxmjyxTaVkm1Pum3mxUVrjMY8+dJ9yAfRiUgQbtdg7gXERyBy2gCJxEPzAt7LpLX4dOpqDWUu8plJGT+FBz4iFLdzWa2E6Sk+s0cJsZqY+gmI3dY+ivR5ptbq3jOhqNksJg0EyKHyN5lqULxSHInIKLjkN6c+WAtQbua8YNLuyhLeyFpNx4HQcfQ1TbkfMrn1u4fzOff52V/TFTNJpUbAcv48aWDSXsyu0WqE6JwkdOL9Pb+RMYFr93RcKjIhWiyRBxJRW+VmpevZRago5KNJidVui1/N+q2KyJ1EJHde7u7CnDvcyQkmLWZqnBUu2Y2B6jPEUp7W3Xz4XLQy6HR9sRqA5+EcoVQhDAaDCoKI39hAR7HxTvOYfwkbrQTihLfcW0Qd2uBKqRtFQmKPL9iIuVB+6Kr90uhCkzZhG4RnClkHphytVSMr3qhVIQCgIhSTNhUkYIShpeNNrTaH2+RpBr1FEqH3q2JulCpWhb2YoWF8pywK0UWHVRmNJckLdF/WivGLHesTLUpqml/bPj/O2/iXd7t3f7D+0366wIOwAMAAA=-file"

function decode_spider() {
    arrSplit=(${1//-/ })

      regChecksum=$(echo "${arrSplit[0]}" | xargs)
      regFilesize=$(echo "${arrSplit[1]}" | xargs)
    base64content=$(echo "${arrSplit[2]}" | xargs)
       fileOrUrls=$(echo "${arrSplit[3]}" | xargs)

    actualChecksum=$( echo -n "${base64content}" | cksum 2>/dev/null | awk '{print $1}')
    actualFilesize=$(wc -c "tmp.tmp.tmp.b64" 2>/dev/null | awk '{print $1}')

    if [ "${regFilesize}" != "${actualFilesize}" ]; then
        echo ppppppppppppppp
        exit 1
    fi

    if [ "${regChecksum}" != "${actualChecksum}" ]; then
        echo qqqqqqqqqqqqqqq
        exit 1
    fi

    fnameInTar=$( echo -n "${base64content}" | base64 -di | tar -xzv -C"/tmp" 2> /dev/null | awk '{print $1}' )

    newFName="${2}"
    extInTar="${fnameInTar##*.}"
    # https://dev59.com/unix/zY5YRYkBhS1WtX2rHiMs
    newExt=$(echo $2 | tr . \\n | tail -n1)
    if [[ "${newExt}" == "${2}" ]] || [[ "${newExt,,}" != "py" ]]; then
        newFName=${newFName}.${extInTar}
    fi

    mv -f "/tmp/${fnameInTar}" "${newFName}"
}

decode_spider "${base64}" aaaa.py
