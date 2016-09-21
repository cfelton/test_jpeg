
import os
import random
import argparse
from argparse import Namespace
import datetime
from fnmatch import fnmatch


def set_default_args(args=None):
    """Set the default test arguments
    Create a Namespace (`args`) and add all the default test arguments
    to the Namespace.  If an `args` Namespace is passed the default 
    test arguments are added if they are missing from the passed `args`.
    The passed `args` existing attributes are unchanged.
    """
    assert args is None or isinstance(args, Namespace)

    if args is None:
        args = Namespace(trace=False, vtrace=False)

    ipth = './test_images/color/'
    ipth = os.path.join(ipth, 'small4.png')

    default_args = (
        ('trace', False), ('vtrace', False), ('vtrace_level', 0),
        ('vtrace_module', 'tb_jpegenc'), ('imgfn', ipth), ('build_only', False),
        ('build_skip_v1', False), ('nout', 0), ('no_wait', False),
        ('dump_bitstreams', False), ('ncyc', 200), )
                    
    # for each of the arguments, if the args doesn't have the attribute
    # add it with the default value above.
    for arg, val in default_args:        
        if not hasattr(args, arg):
            setattr(args, arg, val)

    args.start_time = datetime.datetime.now()

    if not os.path.isdir('output/vcd'):
        os.makedirs('output/vcd')

    return args


def get_cli_args(parser=None):
    """Get the CLI test arguments
    """
    ipth = "./test_images/color/"
    files = os.listdir(ipth)
    files = [ff for ff in files if fnmatch(ff, '*small*')]
    ifn = random.choice(files)
    
    if parser is None:
        parser = argparse.ArgumentParser()

    parser.add_argument('--random_image', action='store_true', default=False,
                        help="use small3.png as test file")
    parser.add_argument('--vtrace', action='store_true', default=False,
                        help="enable Verilog simulator tracing")
    parser.add_argument('--trace', action='store_true', default=False,
                        help="enable MyHDL simulator tracing")

    args = parser.parse_args()

    if args.random_image:
        ipth = os.path.join(ipth, ifn)
    else:
        ipth = os.path.join(ipth, 'small4.png')

    args = set_default_args(args)
    return args
