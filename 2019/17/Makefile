
PYFILE=$(shell basename $(PWD)).py
run: 15.pickle

15.pickle: $(PYFILE) Makefile
	@PYTHONPATH=../common python $(PYFILE) input.txt

test:
	for i in sample_input*.txt input.txt ; do echo $$i ; PYTHONPATH=../common python $(PYFILE) $$i ; done


show: show15.py 15.pickle
	python show15.py
