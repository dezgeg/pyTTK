.PHONY: tests coverage clean default
default: coverage

tests:
	nosetests

coverage: clean
	nosetests --with-cov
	coverage html

clean:
	coverage erase
	rm -rf htmlcov
