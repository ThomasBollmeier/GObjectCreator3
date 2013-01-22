AC_DEFUN([GOC3_CHECK_FOR_FABERSCRIPTORUM], [

# GOC3_CHECK_FOR_FABERSCRIPTORUM(required_min_version, script_file)

	AC_MSG_CHECKING([for faberscriptorum template engine >= $1])
	
	script_call="$2 $1"
	installed_version=`$script_call`
	case $? in
		0)
		AC_MSG_RESULT([yes ($installed_version)])
		;;
		1)
		AC_MSG_RESULT([no])
		AC_MSG_ERROR([faberscriptorum version is too old ($installed_version). 
Get the latest version from http://sourceforge.net/p/faberscriptorum/home/Home/])
		;;
		2)
		AC_MSG_RESULT([no])
		AC_MSG_ERROR([faberscriptorum template engine is required. See http://sourceforge.net/p/faberscriptorum/home/Home/])
		;;
	esac

])
