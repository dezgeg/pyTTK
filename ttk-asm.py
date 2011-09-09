#!/usr/bin/env python
import sys
import argparse

from pyttk.assembler import Assembler
from pyttk.loader.binary_loader import BinaryLoader

def run(args=None):
	parser = argparse.ArgumentParser(description='TTK-91 Assembler')
	parser.add_argument('inputfile', type=argparse.FileType('r'))
	parser.add_argument('outputfile', type=argparse.FileType('w'),  nargs='?',
			default=sys.stdout)

	res = parser.parse_args(args)
	if res:
		binary = Assembler(res.inputfile.name,
				res.inputfile.read()).build_binary()
		BinaryLoader.dump_binary(binary, res.outputfile)

if __name__ == '__main__':
	run()
