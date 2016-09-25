"""
flume command line utility """
import imp
import logging
import os
import warnings

import click

from flume import *
from flume.util import is_string

FLUMERC_LOCATIONS = [
    os.path.join(os.path.expanduser('~'), '.flumerc.py'),
    os.path.join(os.getcwd(), '.flumerc.py'),
]

import flume
VERSION = open(os.path.join(os.path.dirname(flume.__file__),
                            'VERSION')).read().strip()

@click.command()
@click.version_option(version=VERSION)
@click.option('--debug', '-d',
              count=True,
              help='debug mode')
@click.option('--optimize/--no-optimize',
              default=True,
              help='turns read optimizations on/off, default: on')
@click.option('--implicit-sink',
              default=write('stdio'),
              help='defines the default implicit sink, default: write("stdio")')
@click.argument('program')
def main(program=None,
         debug=False,
         optimize=True,
         implicit_sink=None):
    """
    simple command line entry point for executing flume programs
    """
    loglevel = logging.WARN

    if debug:
        loglevel = logging.DEBUG

    with warnings.catch_warnings():
        # lets ignore this silly warning
        message = 'Parent module \'\' not found while handling absolute import'
        warnings.filterwarnings('ignore', message=message)

        for flumerc in FLUMERC_LOCATIONS:
            if os.path.exists(flumerc):
                dirname = os.path.dirname(flumerc)
                fp, pathname, description = imp.find_module('.flumerc', [dirname])
                module = imp.load_module('.flumerc', fp, pathname, description)

                # load those .flumerc goodies into the global scope
                for thing in dir(module):
                    globals()[thing] = module.__dict__[thing]

    if is_string(implicit_sink):
        implicit_sink = eval(implicit_sink)

    eval(program, globals(), locals()).execute(wait=True,
                                               loglevel=loglevel,
                                               optimize=optimize,
                                               implicit_sink=implicit_sink)

if __name__ == '__main__':
    main()
