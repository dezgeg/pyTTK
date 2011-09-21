.PHONY: tests coverage clean default doc run-doc
default: coverage

tests:
	nosetests

coverage: clean
	nosetests --with-cov
	coverage html

clean:
	coverage erase
	rm -rf htmlcov

doc:
	make -C doc html

run-doc: doc
	sensible-browser doc/build/html/index.html &
