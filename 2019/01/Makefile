CPPFLAGS=-g -O0

INPUT_TXT=input.txt

all: part1 part2

part1: 
	gawk '{s += (($$1 - ($$1%3)) / 3) - 2}END{print s}' input.txt

part2: part2.py input.txt
	python part2.py < input.txt

