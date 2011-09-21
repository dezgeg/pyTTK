.PHONY: tests coverage clean default doc run-doc
default: tests

tests:
	nosetests

coverage: clean
	nosetests --with-cov --with-xunit
	coverage html

clean:
	coverage erase
	rm -rf htmlcov

doc:
	make -C doc html

run-doc: doc
	sensible-browser doc/build/html/index.html &
