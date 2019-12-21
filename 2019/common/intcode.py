import os
import sys

do_debug = 'INTCODE_DEBUG' in os.environ

########################################################################
class INTCODE(object):

  def __init__(self,fn):

    with open(fn) as fin:
      self.lt_ints = list(map(int,fin.readline().strip().split(',')))

  def run(self,lt_inputs_arg=[]):
    instance = INSTANCE(self)
    instance.add_input_data(*lt_inputs_arg)
    instance.run()
    return instance


########################################################################
class INSTANCE(object):

  FINI = 99
  READWAIT = 3
  INIT = -1

  POSITION_MODE  = 0
  IMMEDIATE_MODE = 1
  RELATIVE_MODE  = 2

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

  def add_input_data(self,*inputs,**kwargs):
    if (not ('state_must_be_init' in kwargs)) or kwargs['state_must_be_init']:
      assert self.state == INSTANCE.INIT
      assert not self.ip
      assert not self.input_ptr
    self.inputs.extend(inputs)

  def getnext(self
             ,param_mode
             ,no_parse_opcode=True
             ,vmarg=None
             ,iparg=None
             ,allow_exception=True
             ):

    if vmarg is None: vm = self.vm
    else            : vm = vmarg

    if iparg is None: ip = self.ip
    else            : ip = iparg

    try: val = vm[ip]
    except:
      print(dict(ip=ip,len_vm=len(vm)))
      raise

    if do_debug:
      print('getnext({0},no_parse_opcode={1},vmarg={2},iparg={3},allow_exception={4})'
           .format(param_mode
                  ,no_parse_opcode
                  ,vmarg
                  ,iparg
                  ,allow_exception
                  )
           )

    if no_parse_opcode:
      try:
        if INSTANCE.POSITION_MODE==param_mode  : val = vm[val]
        elif INSTANCE.RELATIVE_MODE==param_mode: val = vm[val+self.relative_base]
        else                                   : assert INSTANCE.IMMEDIATE_MODE==param_mode
        if do_debug:
          print('  -> returning {0}'.format((val,ip+1,)))
        return val,ip+1
      except:
        assert allow_exception
        assert vm is self.vm
        assert INSTANCE.POSITION_MODE==param_mode or INSTANCE.RELATIVE_MODE==param_mode
        target_idx = val + (INSTANCE.RELATIVE_MODE==param_mode and self.relative_base or 0)
        assert len(vm) <= target_idx
        self.assign_vm_element(target_idx,0)
        return self.getnext(param_mode
                           ,no_parse_opcode=no_parse_opcode
                           ,vmarg=vmarg
                           ,iparg=iparg
                           ,allow_exception=False
                           )

    opcode = val % 100
    param1 = ((val - opcode) / 100) % 10
    param2 = ((val - (opcode + (100*param1))) / 1000) % 10
    param3 = ((val - (opcode + (100*param1) + (1000*param2))) / 10000) % 10
    param4 = ((val - (opcode + (100*param1) + (1000*param2) + (10000*param3))) / 100000) % 10

    if do_debug:
      print('  -> returning {0}'.format((val,opcode,ip+1,param1,param2,param3,param4,)))
    return val,opcode,ip+1,param1,param2,param3,param4


  def assign_vm_element(self,dest_idx,val,allow_exception=True):
    try:
      self.vm[dest_idx] = val
      if do_debug: print('Assigned self.vm[{0}]<-{1}'.format(dest_idx,val))
    except:
      assert allow_exception
      assert len(self.vm) <= dest_idx
      self.vm += [0] * (1+dest_idx - len(self.vm))
      self.assign_vm_element(dest_idx,val,allow_exception=False)


  def debug_print(self,save_ip):
    if not do_debug: return
    print('ip={0}; save_ip={1}; rel_base={2}; len(vm)={3}; outs={4}; lt_vals={5}'
          .format(self.ip
                 ,save_ip
                 ,self.relative_base
                 ,len(self.vm)
                 ,self.outputs
                 ,self.vm[save_ip:self.ip]
                 )
         )

  def run(self):

    if self.state == INSTANCE.FINI: return

    while True:

      if do_debug: print('')

      save_ip = self.ip

      raw_opcode,opcode,self.ip,p1,p2,p3,p4 = self.getnext(1,no_parse_opcode=False)

      if 99==opcode:                         ### Halt
        self.debug_print(save_ip)
        self.ip = save_ip
        self.state = INSTANCE.FINI
        return

      elif 1==opcode:                        ### Add
        left,self.ip = self.getnext(p1)
        right,self.ip = self.getnext(p2)
        dest_idx,self.ip = self.getnext(INSTANCE.IMMEDIATE_MODE)
        if INSTANCE.RELATIVE_MODE==p3: dest_idx += self.relative_base
        self.debug_print(save_ip)
        self.assign_vm_element(dest_idx,left + right)

      elif 2==opcode:                        ### Multiply
        left,self.ip = self.getnext(p1)
        right,self.ip = self.getnext(p2)
        dest_idx,self.ip = self.getnext(1)
        if INSTANCE.RELATIVE_MODE==p3: dest_idx += self.relative_base
        self.debug_print(save_ip)
        self.assign_vm_element(dest_idx,left * right)

      elif 3==opcode:                        ### Take one input

        if self.input_ptr >= len(self.inputs):
          self.debug_print(save_ip)
          self.ip = save_ip
          self.state = INSTANCE.READWAIT
          return

        dest_idx,self.ip = self.getnext(INSTANCE.IMMEDIATE_MODE)
        if INSTANCE.RELATIVE_MODE==p1: dest_idx += self.relative_base

        input_val,self.input_ptr = self.getnext(INSTANCE.IMMEDIATE_MODE
                                               ,vmarg=self.inputs
                                               ,iparg=self.input_ptr
                                               )
        self.debug_print(save_ip)
        self.assign_vm_element(dest_idx,input_val)

      elif 4==opcode:                        ### Write one output
        val1,self.ip = self.getnext(p1)
        self.debug_print(save_ip)
        self.outputs.append(val1)

      elif 5==opcode:                        ### Jump if True
        val1,self.ip = self.getnext(p1)
        jumpip,self.ip = self.getnext(p2)
        self.debug_print(save_ip)
        if 0 != val1: self.ip = jumpip

      elif 6==opcode:                        ### Jump if False
        val1,self.ip = self.getnext(p1)
        jumpip,self.ip = self.getnext(p2)
        self.debug_print(save_ip)
        if 0 == val1: self.ip = jumpip

      elif 7==opcode:                        ### Less than
        val1,self.ip = self.getnext(p1)
        val2,self.ip = self.getnext(p2)
        dest_idx,self.ip = self.getnext(1)
        if INSTANCE.RELATIVE_MODE==p3: dest_idx += self.relative_base
        self.debug_print(save_ip)
        self.assign_vm_element(dest_idx,val1 < val2 and 1 or 0)

      elif 8==opcode:                        ### Equals
        val1,self.ip = self.getnext(p1)
        val2,self.ip = self.getnext(p2)
        dest_idx,self.ip = self.getnext(1)
        if INSTANCE.RELATIVE_MODE==p3: dest_idx += self.relative_base
        self.debug_print(save_ip)
        self.assign_vm_element(dest_idx,val1 == val2 and 1 or 0)

      elif 9==opcode:                        ### Adjust the relative base
        val1,self.ip = self.getnext(p1)
        self.debug_print(save_ip)
        self.relative_base += val1

      else:
        assert False,'Bad opcode[{0}] (raw={1}) at IP={2}'.format(opcode,raw_opcode,self.ip)


if "__main__"==__name__:
  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  intcode = INTCODE(fn)

  ### Part 1
  print(intcode.run(*[1]))

  ### Part 2
  print(intcode.run(*[5]))
