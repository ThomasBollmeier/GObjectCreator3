AC_PREREQ([2.69])
AC_INIT([gobjectcreator3], [0.8.5], [tbollmeier@web.de])
AC_CONFIG_MACRO_DIR([m4])

AM_INIT_AUTOMAKE([1.11])
AM_SILENT_RULES([yes])
AM_PATH_PYTHON([3.2])

# Dependencies:

GOC3_CHECK_FOR_BOVINUS(
	[1.6.10],
	[$srcdir/m4/bovinus_check.sh]
	)

GOC3_CHECK_FOR_FABERSCRIPTORUM(
	[1.1.0],
	[$srcdir/m4/faberscriptorum_check.sh]
	)

# ------------

AC_OUTPUT([
Makefile
bin/Makefile
doc/Makefile
grammar/Makefile
m4/Makefile
src/Makefile
src/gobjcreator3/Makefile
src/gobjcreator3/__init__.py
src/gobjcreator3/codegen/Makefile
src/gobjcreator3/codegen/templates/Makefile
src/gobjcreator3/model/Makefile
unit-test/Makefile
])
