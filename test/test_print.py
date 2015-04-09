from __future__ import print_function

import sys
import os
import argparse
from argparse import Namespace

def test_print():
  # this is a simple test that demonstrates print output
  # is displayed in travis-ci.  There seems to be an issue
  # when iverilog is used that the python stdout is redirected?
  print("T1: prints work here"); sys.stdout.flush()
  ipth = "./test_images/color/"
  print(os.listdir(ipth)); sys.stdout.flush()
  print("T2: prints work here"); sys.stdout.flush()
  
if __name__ == '__main__':
  test_print()
