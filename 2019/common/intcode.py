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

  def run(self,lt_inputs_arg):
    instance = INSTANCE(self)
    instance.add_input_data(*lt_inputs_arg)
    instance.run()
    return instance


########################################################################
class INSTANCE(object):

  FINI = 99
  READWAIT = 3
  INIT = -1

  def __init__(self,intcode,lt_inputs_arg=None):
    self.vm = [i for i in intcode.lt_ints]
    self.ip = 0
    self.input_ptr = 0
    if isinstance(lt_inputs_arg,list): self.inputs = list(lt_inputs_arg)
    else                             : self.inputs = list()
    self.outputs = list()
    self.state = INSTANCE.INIT

  def make_cascade(self,downstream_instance):
    assert self.state == INSTANCE.INIT
    assert not self.ip
    assert not self.input_ptr
    self.outputs = downstream_instance.inputs

  def add_input_data(self,*inputs):
    assert self.state == INSTANCE.INIT
    assert not self.ip
    assert not self.input_ptr
    self.inputs.extend(inputs)

  def run(self):

    if self.state == INSTANCE.FINI: return

    while True:

      save_ip = self.ip

      raw_opcode,opcode,self.ip,p1,p2,p3,p4 = getnext(self.vm,self.ip,1,no_parse_opcode=False)

      if 99==opcode:                         ### Halt
        self.ip = save_ip
        self.state = INSTANCE.FINI
        return

      elif 1==opcode:                        ### Add
        left,self.ip = getnext(self.vm,self.ip,p1)
        right,self.ip = getnext(self.vm,self.ip,p2)
        dest_idx,self.ip = getnext(self.vm,self.ip,1)
        self.vm[dest_idx] = left + right

      elif 2==opcode:                        ### Multiply
        left,self.ip = getnext(self.vm,self.ip,p1)
        right,self.ip = getnext(self.vm,self.ip,p2)
        dest_idx,self.ip = getnext(self.vm,self.ip,1)
        self.vm[dest_idx] = left * right

      elif 3==opcode:                        ### Take one input

        if self.input_ptr >= len(self.inputs):
          self.ip = save_ip
          self.state = INSTANCE.READWAIT
          return

        input_val,self.input_ptr = getnext(self.inputs,self.input_ptr,1)
        dest_idx,self.ip = getnext(self.vm,self.ip,1)
        self.vm[dest_idx] = input_val

      elif 4==opcode:                        ### Write one output
        val1,self.ip = getnext(self.vm,self.ip,p1)
        self.outputs.append(val1)

      elif 5==opcode:                        ### Jump if True
        val1,self.ip = getnext(self.vm,self.ip,p1)
        jumpip,self.ip = getnext(self.vm,self.ip,p2)
        if 0 != val1: self.ip = jumpip

      elif 6==opcode:                        ### Jump if False
        val1,self.ip = getnext(self.vm,self.ip,p1)
        jumpip,self.ip = getnext(self.vm,self.ip,p2)
        if 0 == val1: self.ip = jumpip

      elif 7==opcode:                        ### Less than
        val1,self.ip = getnext(self.vm,self.ip,p1)
        val2,self.ip = getnext(self.vm,self.ip,p2)
        dest_idx,self.ip = getnext(self.vm,self.ip,1)
        self.vm[dest_idx] = val1 < val2 and 1 or 0

      elif 8==opcode:                        ### Equals
        val1,self.ip = getnext(self.vm,self.ip,p1)
        val2,self.ip = getnext(self.vm,self.ip,p2)
        dest_idx,self.ip = getnext(self.vm,self.ip,1)
        self.vm[dest_idx] = val1 == val2 and 1 or 0

      else:
        assert False,'Bad opcode[{0}] (raw={1}) as IP={2}'.format(opcode,raw_opcode,self.ip)


if "__main__"==__name__:
  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  intcode = INTCODE(fn)

  ### Part 1
  print(intcode.run(*[1]))

  ### Part 2
  print(intcode.run(*[5]))
