#--------------------------------------------
# INSTRUCTION
# Quoted strings are to be filled in by student
#
CCC = "gforth"

clean:
	rm -f compiler stutest.out proftest.out
	ls

stutest.out:
	cat stutest.in
	-${CCC} stutest.in > stutest.out
	cat stutest.out

proftest.out: compiler
	cat proftest.in
	${CCC} proftest.in > proftest.out
	cat proftest.out
