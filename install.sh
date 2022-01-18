#!/usr/bin/bash

# stop on any non-zero exit status
set -o errexit

# test if pip is available
if [ ! -x "$(command -v pip)" ]; then
  # attempt to install it
  pip='python3-pip'
  # try to guess some common package managers to do the install
  # ubuntu/debian types
  if [ -x "$(command -v apt)" ]; then
    installer="sudo apt update && sudo apt install ${pip}"
    printf "%s\n\n" "$installer"
    eval "${installer}"
  # fedora types
  elif [ -x "$(command -v dnf)" ]; then
    installer="sudo dnf install ${pip}"
    printf "%s\n\n" "$installer"
    eval "${installer}"
  # alpine-ish
  elif [ -x "$(command -v apk)" ]; then
    installer="sudo apk add --no-cache ${pip}"
    printf "%s\n\n" "$installer"
    eval "${installer}"
  else
    printf "%s\n\n" "$pip" >&2
    exit 1
  fi
fi

# ensure python dependencies are installed
pip install elemental html5lib htmlmin bs4

# test if geckodriver is available
# doing this with pip/webdriver_manager might be better in future (https://pypi.org/project/webdriver-manager)
if [ ! -x "$(command -v geckodriver)" ]; then
  # attempt to install it
  # get the file (https://github.com/mozilla/geckodriver/releases/latest) and put it in a temp directory
  tmpPath="$(mktemp --directory)"
  # download version 0.30.0 into the tmpPath
  geckoVersion='0.30.0' # should probably work out a dynamic way to get github release assets rather than 'hardocding'
  geckodriverFile="geckodriver-v${geckoVersion}-linux64.tar.gz" # assumes x86_64 systems, will need fixing for arm and other possible deployments
  wget --quiet --directory-prefix="${tmpPath}" "https://github.com/mozilla/geckodriver/releases/download/v${geckoVersion}/${geckodriverFile}"
  if [ -s "${tmpPath}/${geckodriverFile}" ]; then
    # extract the driver to somewhere like /usr/bin or something---use first entry in $PATH
    firstPath="${PATH%%:*}"
    echo "Extracting geckodriver to $firstPath"
    sudo tar -xf "${tmpPath}/${geckodriverFile}" --directory "$firstPath"
  else
    printf "Failed to install geckodriver." >&2
    exit 1
  fi
fi

printf "Software check complete.\n\n"