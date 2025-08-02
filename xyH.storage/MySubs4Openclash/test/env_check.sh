#!/bin/bash

###############################################################################
EnvironmentalCheck() {
    local threadDatetime=$(date "+%Y-%m-%d_%H-%M-%S")"-${RANDOM}-${RANDOM}-$$"

    # https://stackoverflow.com/questions/692000/how-do-i-write-standard-error-to-a-file-while-using-tee-with-a-pipe/692407#692407
    # https://unix.stackexchange.com/questions/352107/generic-way-to-get-temp-path
    mainOut="${TMP_FOLDER:-/tmp}/mainOut.$$" mainErr="${TMP_FOLDER:-/tmp}/mainErr.$$"
    mkfifo "${mainOut}" "${mainErr}"
    trap 'rm "${mainOut}" "${mainErr}"' EXIT
    tee -a "${MAIN_LOG_PATH}" < "${mainOut}" &
    tee -a "${MAIN_LOG_PATH}" < "${mainErr}" >&2 &
    # Example:
    #     wget www.youtube.com -Oytb.html >"$out" 2>"$err"

    # tee
    if ! command -v tee &> /dev/null
    then
        echo "tee could not be found"
        echo "tee could not be found" > "${MAIN_LOG_PATH}"
        exit 1
    fi

    # wget
    if ! command -v wget &> /dev/null
    then
        echo "wget could not be found" >"${mainOut}" 2>"${mainErr}"
        exit 1
    fi

    # curl
    if ! command -v curl &> /dev/null
    then
        echo "curl could not be found" >"${mainOut}" 2>"${mainErr}"
        exit 1
    fi

    # tmp/
    export TMP_FOLDER="${SCRIPT_ROOT_DIR}/tmp"
    if [ ! -d "${TMP_FOLDER}" ]; then
        mkdir -p "${TMP_FOLDER}"
        if [ $? -ne 0 ] || [ ! -d "${TMP_FOLDER}" ]; then
            echo "Failed to mkdir \"${TMP_FOLDER}\"." >"${mainOut}" 2>"${mainErr}"
            exit 1
        fi
    fi

    # log/
    export LOG_FOLDER="${SCRIPT_ROOT_DIR}/log"
    if [ ! -d "${LOG_FOLDER}" ]; then
        mkdir -p "${LOG_FOLDER}"
        if [ $? -ne 0 ] || [ ! -d "${LOG_FOLDER}" ]; then
            echo "Failed to mkdir \"${LOG_FOLDER}\"." >"${mainOut}" 2>"${mainErr}"
            exit 1
        fi
    fi

    # targetYaml/
    export TARGET_YAML_FOLDER="${SCRIPT_ROOT_DIR}/targetYaml"
    if [ ! -d "${TARGET_YAML_FOLDER}" ]; then
        mkdir -p "${TARGET_YAML_FOLDER}"
        if [ $? -ne 0 ] || [ ! -d "${TARGET_YAML_FOLDER}" ]; then
            echo "Failed to mkdir \"${TARGET_YAML_FOLDER}\"." >"${mainOut}" 2>"${mainErr}"
            exit 1
        fi
    fi

    # color.sh
    if [ ! -f "${SCRIPT_ROOT_DIR}/color.sh" ]; then
        echo "File \"${SCRIPT_ROOT_DIR}/color.sh\" does not exist" >"${mainOut}" 2>"${mainErr}"
        exit 1
    fi

    # trim.sh
    if [ ! -f "${SCRIPT_ROOT_DIR}/trim.sh" ]; then
        echo "File \"${SCRIPT_ROOT_DIR}/trim.sh\" does not exist" >"${mainOut}" 2>"${mainErr}"
        exit 1
    fi

    # url_encode.sh
    if [ ! -f "${SCRIPT_ROOT_DIR}/url_encode.sh" ]; then
        echo "File \"${SCRIPT_ROOT_DIR}/url_encode.sh\" does not exist" >"${mainOut}" 2>"${mainErr}"
        exit 1
    fi

    # download_and_extract_url.sh
    if [ ! -f "${SCRIPT_ROOT_DIR}/download_and_extract_url.sh" ]; then
        echo "File \"${SCRIPT_ROOT_DIR}/download_and_extract_url.sh\" does not exist" >"${mainOut}" 2>"${mainErr}"
        exit 1
    fi

    # extract_final_url.sh
    if [ ! -f "${SCRIPT_ROOT_DIR}/extract_final_url.sh" ]; then
        echo "File \"${SCRIPT_ROOT_DIR}/extract_final_url.sh\" does not exist" >"${mainOut}" 2>"${mainErr}"
        exit 1
    fi

    # generalized_download_nodes.sh
    if [ ! -f "${SCRIPT_ROOT_DIR}/generalized_download_nodes.sh" ]; then
        echo "File \"${SCRIPT_ROOT_DIR}/generalized_download_nodes.sh\" does not exist" >"${mainOut}" 2>"${mainErr}"
        exit 1
    fi
}

###############################################################################
EnvironmentalCheck "$@"

################################## End ########################################