import os
import sys
import pickle
import intcode
import itertools

########################################################################
def run_07_part1(lt_phases,input_signal_arg=0):
  """
  OBSOLETE
  Day 7 part 1:  amplifiers in series with phases and inputs,
                 one pass each
  """
  global icode

  ### Input signal will change at each stage
  input_signal = input_signal_arg

  for phase in lt_phases:
    ### Loop over stages
    ### - Create new instance and with phase and input, then run it
    ### - Ensure instance has stopped, ensure there is only one output
    ### - Assign output to input for next stage
    instance = icode.run([phase,input_signal])
    assert instance.state == intcode.INSTANCE.FINI
    assert 1 == len(instance.outputs)
    input_signal = instance.outputs[-1]

  return input_signal
########################################################################

########################################################################
def run_07_part2(lt_phases,input_signal_arg=0):
  """
  Day 7 part 2:  amplifiers in series with phases and inputs,
                 feedback last instance to first,
                 one pass each
 
  """
  global icode

  ### Get length of phases of, and indices into, list 
  N = len(lt_phases)
  R = range(N)

  ### Create an INTCODE INSTANCE stage for each input phase
  instances = [intcode.INSTANCE(icode,lt_inputs_arg=lt_phases[i:i+1])
               for i in R
              ]

  ### Add initial input signal to first stage
  instances[0].add_input_data(input_signal_arg)
  
  ### Cascade stages, including feedback from last to first
  for i in R:
    instances[i].make_cascade(instances[(i+1)%N])

  while True:

    ### Set result counts
    finis = 0
    readwaits = 0

    for instance in instances:

      ### Loop over each stage
      instance.run()

      ### Update stage result counts
      if instance.state==intcode.INSTANCE.READWAIT: readwaits += 1
      elif instance.state==intcode.INSTANCE.FINI  : finis     += 1
      else: assert dict()['{0},{1}'.format(readwaits,finis)]

    ### Continue if all stages expect to read another input
    if N == readwaits:
      for instance in instances:
        assert len(instance.inputs) >= instance.input_ptr
      continue

    assert 0 == readwaits
    assert N == finis
    break
  return instances[-1].outputs[-1]
########################################################################

if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  bn = os.path.basename(fn)

  lt_phase_permutations = list(map(list,itertools.permutations(list(range(5)))))
  icode = intcode.INTCODE(fn)

  if not bn.startswith('sample_input_part2_'):
    print(max(map(run_07_part2,lt_phase_permutations)))

  lt_phase_permutations = list(map(list,itertools.permutations(list(range(5,10)))))

  if not bn.startswith('sample_input_part1_'):
    print(max(map(run_07_part2,lt_phase_permutations)))


