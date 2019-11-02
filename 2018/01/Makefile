 
bothparts: partI partII

partI:
	@echo -n "Part I:  " ; gawk '{s+=$$1}END{print s}' < input.txt 

partII:
	@echo -n "Part II:  "
	@let i=0 ; while [ $$i -lt 140 ] \
	; do let ++i \
	; cat input.txt \
	; done \
	| gawk 'BEGIN{s=0;d[s]++}{s+=$$1}d[s]==1{print s, "after ~" FNR, "lines and ~" FNR/954, "times through the file";exit}{d[s]++}'
