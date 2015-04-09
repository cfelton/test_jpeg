from __future__ import print_function

def test_print():
  # this is a simple test that demonstrates print output
  # is displayed in travis-ci.  There seems to be an issue
  # when iverilog is used that the python stdout is redirected?
  print("do you see me travis?")
  print("If not why?")
  
  
if __name__ == '__main__':
  test_print()
