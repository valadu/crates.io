PYTHON = python


.PHONY: help mypy

help:  ## Print the usage
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

mypy:  ## Check static type for Python
	$(PYTHON) -m mypy lib/

main:  ## Run main program
	$(PYTHON) -m lib 2>stderr.log
