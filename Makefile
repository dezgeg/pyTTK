.PHONY: tests coverage clean default
default: coverage

tests:
	nosetests

coverage: clean
	nosetests --with-coverage
	coverage html --include='tests*,pyttk*' -d htmlcov

clean:
	coverage erase
	rm -rf htmlcov
