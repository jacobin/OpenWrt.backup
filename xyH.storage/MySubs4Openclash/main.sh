#!/bin/bash

###############################################################################
function fnTask() {
    local name="$1"
    local refUrl="$2"

    local threadDatetime=$(date "+%Y-%m-%d_%H-%M-%S")"-${RANDOM}-${RANDOM}-$$"

    # https://stackoverflow.com/questions/692000/how-do-i-write-standard-error-to-a-file-while-using-tee-with-a-pipe/692407#692407
    # https://unix.stackexchange.com/questions/352107/generic-way-to-get-temp-path
    out="${TMP_FOLDER:-/tmp}/out.$$" err="${TMP_FOLDER:-/tmp}/err.$$"
    mkfifo "$out" "$err"
    trap 'rm "$out" "$err"' EXIT
    tee -a "${LOG_FOLDER}/${name}.${threadDatetime}.stdout.log" < "$out" &
    tee -a "${LOG_FOLDER}/${name}.${threadDatetime}.stderr.log" < "$err" >&2 &
    # Example:
    #     wget www.youtube.com -Oytb.html >"$out" 2>"$err"

    outSuburl=
    source "${SCRIPT_ROOT_DIR}/extract_final_url.sh" "-u${refUrl}" "-foutSuburl"
    if [ $? -ne 0 ]; then
        return 1
    fi
    #source "${SCRIPT_ROOT_DIR}/generalized_download_nodes.sh" "-c${SUBCONVERTER}" "-u${outSuburl}" "-n${name}" "-t${threadDatetime}"
    wget "${outSuburl}" "-O${TARGET_DOWNLOAD_FOLDER}/${name}"
    if [ $? -ne 0 ]; then
        printf "%s, wget download \"%s -- %s\" failed.\n" "$FUNCNAME" "${name}" "${outSuburl}" >"$out" 2>"$err"
        return 1
    fi
}

###############################################################################
function fnEnvironmentalCheck() {
    # check NOW_DATE_TIME #################################################
    if [ -z "${NOW_DATE_TIME}" ]; then
      echo Environment variable \"NOW_DATE_TIME\" is empty.
      exit 1
    fi

    # check SCRIPT_ROOT_DIR ###############################################
    if [ -z "${SCRIPT_ROOT_DIR}" ]; then
      echo Environment variable \"SCRIPT_ROOT_DIR\" is empty.
      exit 1
    fi

    # TMP_FOLDER ##########################################################
    export TMP_FOLDER="${SCRIPT_ROOT_DIR}/tmp"
    if [ ! -d "${TMP_FOLDER}" ]; then
        mkdir -p "${TMP_FOLDER}"
        if [ $? -ne 0 ] || [ ! -d "${TMP_FOLDER}" ]; then
            echo "Failed to mkdir \"${TMP_FOLDER}\"." >"$out" 2>"$err"
            exit 1
        fi
    fi

    # LOG_FOLDER ##########################################################
    export LOG_FOLDER="${SCRIPT_ROOT_DIR}/log"
    if [ ! -d "${LOG_FOLDER}" ]; then
        mkdir -p "${LOG_FOLDER}"
        if [ $? -ne 0 ] || [ ! -d "${LOG_FOLDER}" ]; then
            echo "Failed to mkdir \"${LOG_FOLDER}\"." >"$out" 2>"$err"
            exit 1
        fi
    fi

    # MAIN_THREAD_LOG_PATH ################################################
    ## https://stackoverflow.com/questions/192319/how-do-i-know-the-script-file-name-in-a-bash-script
    ## https://stackoverflow.com/questions/965053/extract-filename-and-extension-in-bash
    local fileNameExt=$(basename $BASH_SOURCE)
    local fileName="${fileNameExt%.*}"
    export MAIN_THREAD_LOG_PATH="${LOG_FOLDER}/${fileName}.${NOW_DATE_TIME}.log"

    # tee #################################################################
    if ! command -v tee &> /dev/null
    then
        echo "tee could not be found"
        echo "tee could not be found" > "${MAIN_THREAD_LOG_PATH}"
        exit 1
    fi
    ## https://stackoverflow.com/questions/692000/how-do-i-write-standard-error-to-a-file-while-using-tee-with-a-pipe/692407#692407
    ## https://unix.stackexchange.com/questions/352107/generic-way-to-get-temp-path
    out="${TMP_FOLDER:-/tmp}/out.$$" err="${TMP_FOLDER:-/tmp}/err.$$"
    mkfifo "$out" "$err"
    trap 'rm "$out" "$err"' EXIT
    tee -a "${MAIN_THREAD_LOG_PATH}" < "$out" &
    tee -a "${MAIN_THREAD_LOG_PATH}" < "$err" >&2 &
    ## Example:
    ##     wget www.youtube.com -Oytb.html >"$out" 2>"$err"

    # wget ################################################################
    if ! command -v wget &> /dev/null
    then
        echo "wget could not be found" >"$out" 2>"$err"
        exit 1
    fi

    # curl ################################################################
    if ! command -v curl &> /dev/null
    then
        echo "curl could not be found" >"$out" 2>"$err"
        exit 1
    fi

    ##### mv -f "${TARGET_DOWNLOAD_FOLDER}" "${TARGET_DOWNLOADBAK_FOLDER}/"

    # color.sh
    if [ ! -f "${SCRIPT_ROOT_DIR}/color.sh" ]; then
        echo "File \"${SCRIPT_ROOT_DIR}/color.sh\" does not exist" >"$out" 2>"$err"
        exit 1
    fi

    # trim.sh
    if [ ! -f "${SCRIPT_ROOT_DIR}/trim.sh" ]; then
        echo "File \"${SCRIPT_ROOT_DIR}/trim.sh\" does not exist" >"$out" 2>"$err"
        exit 1
    fi

    # url_encode.sh
    if [ ! -f "${SCRIPT_ROOT_DIR}/url_encode.sh" ]; then
        echo "File \"${SCRIPT_ROOT_DIR}/url_encode.sh\" does not exist" >"$out" 2>"$err"
        exit 1
    fi

    # assert.sh
    if [ ! -f "${SCRIPT_ROOT_DIR}/assert.sh" ]; then
        echo "File \"${SCRIPT_ROOT_DIR}/assert.sh\" does not exist" >"$out" 2>"$err"
        exit 1
    fi

    # download_and_extract_url.sh
    if [ ! -f "${SCRIPT_ROOT_DIR}/download_and_extract_url.sh" ]; then
        echo "File \"${SCRIPT_ROOT_DIR}/download_and_extract_url.sh\" does not exist" >"$out" 2>"$err"
        exit 1
    fi

    # extract_final_url.sh
    if [ ! -f "${SCRIPT_ROOT_DIR}/extract_final_url.sh" ]; then
        echo "File \"${SCRIPT_ROOT_DIR}/extract_final_url.sh\" does not exist" >"$out" 2>"$err"
        exit 1
    fi

#    # generalized_download_nodes.sh
#    if [ ! -f "${SCRIPT_ROOT_DIR}/generalized_download_nodes.sh" ]; then
#        echo "File \"${SCRIPT_ROOT_DIR}/generalized_download_nodes.sh\" does not exist" >"$out" 2>"$err"
#        exit 1
#    fi
}

###############################################################################
function fnMergeAndConvert() {
    # https://stackoverflow.com/questions/1063347/passing-arrays-as-parameters-in-bash
    # https://stackoverflow.com/questions/29047183/define-a-local-array-in-a-bash-function-and-access-it-outside-that-function
    declare -a filesArr=("${!2}") || exit 1
    local mergeResult="$1"

    source "${SCRIPT_ROOT_DIR}/trim.sh"
    source "${SCRIPT_ROOT_DIR}/url_encode.sh"
    source "${SCRIPT_ROOT_DIR}/assert.sh"

    # subConverter, fileAssistant
    local subConverter="http://127.0.0.1:25500"
    local fileAssistant="http://192.168.5.1/cgi-bin/luci/admin/nas/fileassistant"

    # subUrls
#   local subUrls=
#   local FILES="${TARGET_DOWNLOAD_FOLDER}/*"
#   for f in ${FILES}; do
#       subUrls=$(printf '%s|${fileAssistant}?path=%s' "${subUrls}" "${f}")
#   done
#   subUrls=$( echo "$subUrls" | trim ' ' | trim '|' | trim ' ' )

    # fILTER, eXCLUDE
    local fILTER="function%20filter%28node%29%20%7B%0A%20%20%20%20if%28node.Type."`
                `"toLowerCase%28%29%20%3D%3D%3D%20%22ss%22%20%26%26%20node.Encryp"`
                `"tMethod.toLowerCase%28%29%20%3D%3D%3D%20%22chacha20-poly1305%22"`
                `"%29%20%7B%0A%20%20%20%20%20%20%20%20return%20false%3B%0A%20%20%"`
                `"20%20%7D%0A%20%20%20%20return%20true%3B%0A%7D"
    local eXCLUDE="%28%E4%B8%AD%E5%9C%8B%7C%E9%A6%99%E6%B8%AF%7C%E4%B8%AD%E5%9B%B"`
                 `"D%7CCN%7CHK%7CHong%20Kong%7CHongKong%7C%E5%B9%BF%E4%B8%9C%7C%E"`
                 `"8%B4%B5%E5%B7%9E%7C%E5%8C%97%E4%BA%AC%7C%E4%B8%8A%E6%B5%B7%7C%"`
                 `"E7%A7%BB%E5%8A%A8%7Cv2cross%29"

    # urlPrefix
    ## https://stackoverflow.com/questions/7729023/how-do-i-break-up-an-extremely-long-string-literal-in-bash
    local urlPrefix="${subConverter}/sub?target=clash"`
                                      `"&config=ACL4SSR_Online_Full_AdblockPlus.ini"`
                                      `"&enable_filter=true"`
                                      `"&filter_script=${fILTER}"`
                                      `"&exclude=${eXCLUDE}"`
                                      `"&append_type=true"`
                                      `"&emoji=true"`
                                      `"&list=false"`
                                      `"&udp=true"`
                                      `"&tfo=true"`
                                      `"&scv=true"`
                                      `"&fdn=true"
    local -a nextLevel

    local arraySize=${#filesArr[@]}
    assert "${arraySize} -ge 1" $LINENO
    local groupCount=$(( (arraySize + 10 -1)/10 ))
    assert "${groupCount} -ge 1" $LINENO

    # https://unix.stackexchange.com/questions/527356/can-one-declare-multiple-local-variables-in-one-line
    local i, j, k=0, ii=0
    for ((i = 0 ; i < ${groupCount} ; i++ )); do
        local subUrls=
        for ((j = 0 ; j < 10 && k < ${arraySize} ; j++, k++ )); do
            subUrls=$(printf "%s|${fileAssistant}?path=%s" "${subUrls}" "${filesArr[i*10+j]}")
        done
        subUrls=$( echo "$subUrls" | trim ' ' | trim '|' | trim ' ' )

        # base64Suburl
        local base64Suburl=`fnUrlEncode "${subUrls}"`

        # finalSuburl
        local finalSuburl="${urlPrefix}&url=${base64Suburl}"

        local threadDatetime=$(date "+%Y-%m-%d_%H-%M-%S")"-${RANDOM}-${RANDOM}-$$"
        local tmpYaml="${TMP_FOLDER}/${threadDatetime}.yml"
        wget "${finalSuburl}" -O"${tmpYaml}"
        if [ $? -eq 0 ]; then
            nextLevel[ii]="${tmpYaml}"
            let ii++
        fi
    done

    assert "${ii} -ge 0" $LINENO

    if [ "${ii}" -eq 0 ]; then
        printf "%s failed." "$FUNCNAME" >"$out" 2>"$err"
        exit 1
    fi

    if [ "${ii}" -eq 1 ]; then
        eval "${mergeResult}=${nextLevel[0]}"
        return 0
    fi

    fnMergeAndConvert "${mergeResult}" "nextLevel[@]"
}

###############################################################################
function fnMain() {
    # https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script?page=1&tab=scoredesc#%E2%80%A6
    export SCRIPT_ROOT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

    export NOW_DATE_TIME=$(date "+%Y-%m-%d_%H-%M-%S")

    fnEnvironmentalCheck

    source "${SCRIPT_ROOT_DIR}/color.sh"

    local usage="Usage: \n\t$(basename $BASH_SOURCE) <${Red}-c${Color_Off}SubConverter> <${Red}-f${Color_Off}DbFile> <${Red}-h${Color_Off}>"`
                `"\n\tExample:"`
                `"\n\t\t./$(basename $BASH_SOURCE) ${Red}-c${Color_Off}${UPurple}http://127.0.0.1:25500${Color_Off} ${Red}-f${Color_Off}${IYellow}definition_file.txt${Color_Off}"`
                `"\n\tNote:"`
                `"\n\t\tSubConverter\t-- Such as \"${UPurple}http://127.0.0.1:25500${Color_Off}\" or \"${UPurple}https://api.dler.io${Color_Off}\""`
                `"\n\t\tDbFile\t\t-- A library file such as ${IYellow}definition_file.txt${Color_Off} with multi-line content similar to the following line"`
                `"\n\t\t\t\t\t${BIRed}xfxssr${Color_Off};${UGreen}https://raw.githubusercontent.com/xfxssr/ssnode/main/README.md${Color_Off}"`
                `"\n\t\t\t\t\t${BIRed}ChromeGo01${Color_Off};${UGreen}https://gitlab.com/free9999/ipupdate/-/raw/master/clash/config.yaml${Color_Off}"`
                `"\n"

    local OPTIND
    local dbFile
    export SUBCONVERTER
    local flag

    # https://www.baeldung.com/linux/use-command-line-arguments-in-bash-script
    while getopts ":f:c:h" flag
    do
        case "${flag}" in
            f) dbFile=${OPTARG};;
            c) SUBCONVERTER=${OPTARG};;
            h) printf "${usage}\n" >"$out" 2>"$err"
               exit
               ;;
            :) printf "missing argument for -%s\n" "${OPTARG}" >"$out" 2>"$err"
               printf "${usage}\n" >"$out" 2>"$err"
               exit 1
               ;;
           \?) printf "illegal option: -%s\n" "${OPTARG}" >"$out" 2>"$err"
               printf "${usage}\n" >"$out" 2>"$err"
               exit 1
               ;;
            *) printf "${usage}\n" >"$out" 2>"$err"
               exit 1
               ;;
        esac
    done
    shift $(( OPTIND - 1 ))

    if [ -z "${dbFile}" ] || [ -z "${SUBCONVERTER}" ]; then
        printf "${usage}\n" >"$out" 2>"$err"
        exit 1
    fi

    # ${dbFile}
    if [ ! -f "${dbFile}" ]; then
        echo "The definition file \"${dbFile}\" does not exist" >"$out" 2>"$err"
        exit 1
    fi

    #https://unix.stackexchange.com/questions/190163/shell-command-script-to-see-if-a-host-is-alive
    if [ ! curl -I "${SUBCONVERTER}" > /dev/null 2>&1 ]; then
        echo "\"${SUBCONVERTER}\" offline or web server problem." >"$out" 2>"$err"
        exit 1
    fi

    # https://blog.51cto.com/u_15911260/5934639 -------------------------------
    local Nproc=5               # 可同时运行的最大作业数
    local Pfifo="/tmp/$$.fifo"  # 以PID为名，防止创建命名管道时与已有文件重名，从而失败
    mkfifo $Pfifo               # 创建命名管道
    exec 6<>$Pfifo              # 以读写方式打开命名管道，文件标识符fd为6
                                # fd可取除0，1，2，5外0-9中的任意数字
    rm -f $Pfifo                # 删除文件，也可不删除，不影响后面操作

    # 在fd6中放置$Nproc个空行作为令牌
    local i
    for((i=1; i<=$Nproc; i++)); do
        echo
    done >&6
    # -------------------------------------------------------------------------

    # fnTask
    # https://stackoverflow.com/questions/12916352/shell-script-read-missing-last-line
    local line
    cat "${dbFile}" | while read line || [ -n "$line" ];
    do
        line=$(echo ${line} | xargs)
        if [[ ${line:0:1} == "#" ]]; then
            continue
        fi

        local name=$(echo ${line} | cut -d \; -f 1)
        local refUrl=$(echo ${line} | cut -d \; -f 2)

        name=$(echo ${name} | xargs)
        refUrl=$(echo ${refUrl} | xargs)

        # https://blog.51cto.com/u_15911260/5934639 -------------------
        read -u6                # 领取令牌，即从fd6中读取行，每次一行
                                # 对管道，读一行便少一行，每次只能读取一行
                                # 所有行读取完毕，执行挂起，直到管道再次有可读行
                                # 因此实现了进程数量控制
        {                       # 要批量执行的命令放在大括号内，后台运行
            fnTask "${name}" "${refUrl}" && \
            {                   # 可使用判断子进程成功与否的语句
                echo "Job \"${name}\" finished" >"$out" 2>"$err"
            } || \
            {
                echo "Job \"${name}\" error" >"$out" 2>"$err"
            }
            sleep 1             # 暂停1秒，可根据需要适当延长，
                                # 关键点，给系统缓冲时间，达到限制并行进程数量的作用
            echo >&6            # 归还令牌，即进程结束后，再写入一行，使挂起的循环继续执行
        } &
        # -------------------------------------------------------------
    done

    # https://stackoverflow.com/questions/35995670/list-only-file-names-in-directories-and-subdirectories-in-bash
    # https://superuser.com/questions/527535/how-do-i-list-files-with-full-paths-in-linux
    # https://stackoverflow.com/questions/27340307/list-file-using-ls-command-in-linux-with-full-path
    # https://stackoverflow.com/questions/9954680/how-to-store-directory-files-listing-into-an-array
    # https://stackoverflow.com/questions/10574794/how-to-list-only-files-and-not-directories-of-a-directory-bash
    local i=0; while read line
    do
        filesArray[ i ]="$line"
        #echo ${filesArray[i]}
        (( i++ ))
    done < <( find "${TARGET_DOWNLOAD_FOLDER}" -maxdepth 1 -type f )

    if [ "${i}" -eq 0 ]; then
        printf "The number of files downloaded is 0" >"$out" 2>"$err"
        exit 1
    fi
    assert "${i} -ge 1" $LINENO

    fnMergeAndConvert "mergeResult" "filesArray[@]"
    if [ $? -ne 0 ]; then
        exit 1
    fi

    local targetYaml="${TARGET_YAML_FOLDER}/super_node_collection.yml"
    rm -f "${targetYaml}"
    # https://stackoverflow.com/questions/525592/find-and-replace-inside-a-text-file-from-a-bash-command
    sed 's/cipher: chacha20-poly1305/cipher: chacha20-ietf-poly1305/g' < "${mergeResult}" > "${targetYaml}"
}

###############################################################################
# https://stackoverflow.com/questions/1878882/how-do-i-create-an-array-in-unix-shell-scripting
#   Unquoted, $@ is the same as $*; the difference only shows up when quoted: "$*" is one word, while "$@" preserves the original word breaks.
fnMain "$@"

################################## End ########################################
