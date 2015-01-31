compiler:
	echo "No compile step is required because Python is being used."
	echo "Copying program into the file called "compiler" anyway."
	cp lexer.py compiler

clean:
	rm -f compiler stutest.out proftest.out
	ls

stutest.out: compiler
	bash runtests.sh > stutest.out
	cat stutest.out

proftest.out: compiler
	cat $(PROFTEST)
	compiler $(PROFTEST) > proftest.out
	cat proftest.out
