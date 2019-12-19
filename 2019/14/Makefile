
PYFILE=$(shell basename $(PWD)).py
run: 13.pickle

13.pickle:
	@PYTHONPATH=../common python $(PYFILE) input.txt

test:
	for i in sample_input*.txt input.txt ; do echo $$i ; PYTHONPATH=../common python $(PYFILE) $$i ; done


play: play13.py 13.pickle
	clear
	python play13.py
