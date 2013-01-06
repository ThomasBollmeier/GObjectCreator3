SUBDIRS = codegen model

gobjcreator3dir = $(pythondir)/gobjcreator3

dist_gobjcreator3_DATA = \
	ast_visitor.py \
	compiler.py \
	interpreter.py \
	misc.py \
	parameter.py \
	parser.py \
	preprocessor.py
	
nodist_gobjcreator3_DATA = __init__.py

EXTRA_DIST = __init__.py.in 

uninstall-local:
	-rm -rf $(gobjcreator3dir)

