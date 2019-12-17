import os
import sys
import pickle
import intcode

########################################################################
if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  bn = os.path.basename(fn)
  icode = intcode.INTCODE(fn)

  if not bn.startswith('sample_input_part2_'):
    instance = icode.run([1])
    print((instance.inputs,instance.input_ptr,instance.outputs,))
