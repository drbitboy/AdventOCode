
PYFILE=$(shell basename $(PWD)).py
run:
	@python $(PYFILE) input.txt

test:
	for i in sample_input*.txt input.txt ; do echo $$i ; python $(PYFILE) $$i ; done
