AC_DEFUN([GOC3_CHECK_FOR_BOVINUS],[

# GOC3_CHECK_FOR_BOVINUS(required_min_version, script_file)

	AC_MSG_CHECKING([for bovinus parser library >= $1])
	
	script_call="$2 $1"
	installed_version=`$script_call`
	case $? in
		0)
		AC_MSG_RESULT([yes ($installed_version)])
		;;
		1)
		AC_MSG_RESULT([no])
		AC_MSG_ERROR([bovinus version is too old ($installed_version).
Get the latest version from https://github.com/ThomasBollmeier/bovinus])
		;;
		2)
		AC_MSG_RESULT([no])
		AC_MSG_ERROR([bovinus parser library is required. See https://github.com/ThomasBollmeier/bovinus])
		;;
	esac
	
])
