import argparse
import sys
import os
import logging
from python_ls import PythonLanguageServer

log = logging.getLogger(__name__)
logging.basicConfig(
    level = logging.INFO,
    filename = './server.log',
    filemode = 'w',
    format = '%(name)s %(funcName)s %(levelname)s: %(message)s')


def _binary_stdio():  
    # need to add a judge to recognize the version of python
    # the default of here is python3
    stdin, stdout = sys.stdin.buffer, sys.stdout.buffer
    return stdin, stdout


def main():
    log.info("Welcome to mypy languageserver")
    stdin, stdout = _binary_stdio()
    languageserver = PythonLanguageServer(stdin, stdout)
    languageserver.run()


main()
    