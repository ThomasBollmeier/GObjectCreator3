#!/bin/bash

# --> required version string "x.y.z"
# <-- 0: installed version >= required version
#     1: installed version too old
#     2: no faberscriptorum library found

function split () {

	local parts
	prev_IFS=$IFS
	IFS="."
	read -a parts <<< "$1"
	IFS=$sprev_IFS

	echo ${parts[@]}
	
}

fs_info=`python3 -c "import faberscriptorum as fs; print(fs.API.VERSION)" 2>/dev/null`
if [ -z "$fs_info" ]; then
	echo ""
	exit 2
fi

#
# Get installed bovinus version:
#
fs_version=`echo $fs_info | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+'`

declare -a installed_version
installed_version=($(split $fs_version))

typeset -i installed_major_version
typeset -i installed_minor_version
typeset -i installed_patch

installed_major_version=${installed_version[0]}
installed_minor_version=${installed_version[1]}
installed_patch=${installed_version[2]}

#
# Compare with required version
# 

declare -a required_version
required_version=($(split $1))

typeset -i required_major_version
typeset -i required_minor_version
typeset -i required_patch

required_major_version=${required_version[0]}
required_minor_version=${required_version[1]}
required_patch=${required_version[2]}

if [ "$installed_major_version" -gt "$required_major_version" ]; then
	echo $fs_version
	exit 0
else if [ "$installed_major_version" -lt "$required_major_version" ]; then
	echo $fs_version
	exit 1
	fi
fi

if [ "$installed_minor_version" -gt "$required_minor_version" ]; then
	echo $fs_version
	exit 0
else if [ "$installed_minor_version" -lt "$required_minor_version" ]; then
	echo $fs_version
	exit 1
	fi
fi

if [ "$installed_patch" -ge "$required_patch" ]; then
	echo $fs_version
	exit 0
else
	echo $fs_version
	exit 1
fi
