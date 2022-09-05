PYTHON = python


.PHONY: help readme mypy data

help:    ## Print the usage
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

readme:  ## Create or update README.md
	$(PYTHON) -m data

mypy:    ## Check static type for Python
	$(PYTHON) -m mypy lib/

data:    ## Run main program in lib library to collect data
	$(PYTHON) -m lib 2>stderr.log
