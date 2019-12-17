import os
import sys


########################################################################
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
    self.relative_base = 0

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


  def getnext(self
             ,param_mode
             ,vmarg=None
             ,iparg=None
             ,no_parse_opcode=True
             ):

    if vmarg is None: vm = self.vm
    else            : vm = vmarg

    if iparg is None: ip = self.ip
    else            : ip = iparg

    val = vm[ip]

    if no_parse_opcode:
      if 0==param_mode  : val = vm[val]
      elif 2==param_mode: val = vm[val+self.relative_base]
      else              : assert 1==param_mode
      return val,ip+1

    opcode = val % 100
    param1 = ((val - opcode) / 100) % 10
    param2 = ((val - (opcode + (100*param1))) / 1000) % 10
    param3 = ((val - (opcode + (100*param1) + (1000*param2))) / 10000) % 10
    param4 = ((val - (opcode + (100*param1) + (1000*param2) + (10000*param3))) / 100000) % 10

    return val,opcode,ip+1,param1,param2,param3,param4


  def run(self):

    if self.state == INSTANCE.FINI: return

    while True:

      save_ip = self.ip

      raw_opcode,opcode,self.ip,p1,p2,p3,p4 = self.getnext(1,self.vm,self.ip,no_parse_opcode=False)

      if 99==opcode:                         ### Halt
        self.ip = save_ip
        self.state = INSTANCE.FINI
        return

      elif 1==opcode:                        ### Add
        left,self.ip = self.getnext(p1,self.vm,self.ip)
        right,self.ip = self.getnext(p2,self.vm,self.ip)
        dest_idx,self.ip = self.getnext(1,self.vm,self.ip)
        self.vm[dest_idx] = left + right

      elif 2==opcode:                        ### Multiply
        left,self.ip = self.getnext(p1,self.vm,self.ip)
        right,self.ip = self.getnext(p2,self.vm,self.ip)
        dest_idx,self.ip = self.getnext(1,self.vm,self.ip)
        self.vm[dest_idx] = left * right

      elif 3==opcode:                        ### Take one input

        if self.input_ptr >= len(self.inputs):
          self.ip = save_ip
          self.state = INSTANCE.READWAIT
          return

        input_val,self.input_ptr = self.getnext(1,self.inputs,self.input_ptr)
        dest_idx,self.ip = self.getnext(1,self.vm,self.ip)
        self.vm[dest_idx] = input_val

      elif 4==opcode:                        ### Write one output
        val1,self.ip = self.getnext(p1,self.vm,self.ip)
        self.outputs.append(val1)

      elif 5==opcode:                        ### Jump if True
        val1,self.ip = self.getnext(p1,self.vm,self.ip)
        jumpip,self.ip = self.getnext(p2,self.vm,self.ip)
        if 0 != val1: self.ip = jumpip

      elif 6==opcode:                        ### Jump if False
        val1,self.ip = self.getnext(p1,self.vm,self.ip)
        jumpip,self.ip = self.getnext(p2,self.vm,self.ip)
        if 0 == val1: self.ip = jumpip

      elif 7==opcode:                        ### Less than
        val1,self.ip = self.getnext(p1,self.vm,self.ip1)
        val2,self.ip = self.getnext(p2,self.vm,self.ip)
        dest_idx,self.ip = self.getnext(1,self.vm,self.ip)
        self.vm[dest_idx] = val1 < val2 and 1 or 0

      elif 8==opcode:                        ### Equals
        val1,self.ip = self.getnext(p1,self.vm,self.ip)
        val2,self.ip = self.getnext(p2,self.vm,self.ip)
        dest_idx,self.ip = self.getnext(1,self.vm,self.ip)
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
