import os
import sys


def getnext(vmarg,iparg,param_mode,no_parse_opcode=True):

  val = vmarg[iparg]

  if no_parse_opcode:
    if 0==param_mode: val = vmarg[val]
    return val,iparg+1

  opcode = val % 100
  param1 = ((val - opcode) / 100) % 10
  param2 = ((val - (opcode + (100*param1))) / 1000) % 10
  param3 = ((val - (opcode + (100*param1) + (1000*param2))) / 10000) % 10
  param4 = ((val - (opcode + (100*param1) + (1000*param2) + (10000*param3))) / 100000) % 10

  return val,opcode,iparg+1,param1,param2,param3,param4


class INTCODE(object):

  def __init__(self,fn):
  
    with open(fn) as fin:
      self.lt_ints = list(map(int,fin.readline().strip().split(',')))

  def run(self,*inputs):

    outputs = list()
    vm = [i for i in self.lt_ints]
    ip = 0
    input_ptr = 0

    while True:
      raw_opcode,opcode,ip,p1,p2,p3,p4 = getnext(vm,ip,1,no_parse_opcode=False)
      dt = dict(raw_opcode=raw_opcode
               ,opcode=opcode
               ,ip=ip,p1=p1,p2=p2,p3=p3,p4=p4
               )

      if 99==opcode:                         ### Halt
        return outputs,vm

      elif 1==opcode:                        ### Add
        left,ip = getnext(vm,ip,p1)
        right,ip = getnext(vm,ip,p2)
        dest_idx,ip = getnext(vm,ip,1)
        vm[dest_idx] = left + right

      elif 2==opcode:                        ### Multiply
        left,ip = getnext(vm,ip,p1)
        right,ip = getnext(vm,ip,p2)
        dest_idx,ip = getnext(vm,ip,1)
        vm[dest_idx] = left * right

      elif 3==opcode:                        ### Take one input
        input_val,input_ptr = getnext(inputs,input_ptr,1)
        dest_idx,ip = getnext(vm,ip,1)
        vm[dest_idx] = input_val

      elif 4==opcode:                        ### Write one output
        val1,ip = getnext(vm,ip,p1)
        outputs.append(val1)

      elif 5==opcode:                        ### Jump if True
        val1,ip = getnext(vm,ip,p1)
        jumpip,ip = getnext(vm,ip,p2)
        if 0 != val1: ip = jumpip

      elif 6==opcode:                        ### Jump if False
        val1,ip = getnext(vm,ip,p1)
        jumpip,ip = getnext(vm,ip,p2)
        if 0 == val1: ip = jumpip

      elif 7==opcode:                        ### Less than
        val1,ip = getnext(vm,ip,p1)
        val2,ip = getnext(vm,ip,p2)
        dest_idx,ip = getnext(vm,ip,1)
        vm[dest_idx] = val1 < val2 and 1 or 0

      elif 8==opcode:                        ### Equals
        val1,ip = getnext(vm,ip,p1)
        val2,ip = getnext(vm,ip,p2)
        dest_idx,ip = getnext(vm,ip,1)
        vm[dest_idx] = val1 == val2 and 1 or 0

      else:
        assert False,'Bad opcode[{0}] (raw={1}) as IP={2}'.format(opcode,raw_opcode,ip)


if "__main__"==__name__:
  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  intcode = INTCODE(fn)

  ### Part 1
  print(intcode.run(*[1]))

  ### Part 2
  print(intcode.run(*[5]))
