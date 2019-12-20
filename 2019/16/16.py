import os
import sys

do_debug = 'DEBUG' in os.environ

base_pattern = [0,1,0,-1]

def bpdup(ioffset): return sum( [[v]*(ioffset+1) for v in base_pattern],[])

def bpget(ioffset,L):
  bpbase = bpdup(ioffset)
  Lbpbase = len(bpbase)
  return [bpbase[i%Lbpbase] for i in range(1,L+1)]
  
def icalc(*lts):
  prods = [e*p for e,p in zip(*lts)]
  sumneg = sum([-prod for prod in prods if prod < 0])
  sumpos = sum([prod for prod in prods if prod > 0])
  if do_debug: print(dict(icalc=dict(lts=lts,prods=prods,sumneg=sumneg,sumpos=sumpos)))
  return abs(sumpos - sumneg) % 10

Join16 = lambda lt: ''.join(['{0}'.format(i) for i in lt])

########################################################################
def part1(inputs,phases):
  """
  Day 16 part 1

  """

  lt_elements = list(map(int,inputs))

  phase,L = 0,len(lt_elements) 

  while phase < phases:
    phase += 1
    lt_elements = [icalc(lt_elements,bpget(ioffset,L)) for ioffset in range(L)]
    if do_debug and not (phase%10): sys.stdout.write('.'); sys.stdout.flush()
  
  return dict(result8=Join16(lt_elements[:8]),result=Join16(lt_elements),L=L,phases=phases,inputs=inputs)


########################################################################
def part2(inputs,phases,Ndups=10000,Noffset_digits=7):
  """
  Day 15 part 2

  """
  lt_elements = list(map(int,inputs))
  phase,L = 0,len(lt_elements)
  skip = int(Join16(lt_elements[:Noffset_digits]))
  L10k = L * Ndups
  remainder = L10k - skip
  Rremainder = range(remainder)
  assert remainder < (L10k>>1)
  lt_tmp = list(map(int,inputs))
  lt_tmp.reverse()
  lt_elements_rev = [lt_tmp[i%L] for i in Rremainder]

  print((len(lt_elements_rev),lt_elements_rev[:10],))

  while phase < phases:
    phase += 1
    cumsum = 0
    for i in Rremainder:
      lt_elements_rev[i] += i and lt_elements_rev[i-1] or 0

  lt_elements_8 = [v%10 for v in lt_elements_rev[-8:]]
  lt_elements_8.reverse()

  return dict(result8=Join16(lt_elements_8),L=L,phases=phases,inputs=inputs,Ndups=Ndups,remainder=remainder)


########################################################################

if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  bn = os.path.basename(fn)

  with open(fn,'r') as fin:
    s_lt_elements_0 = fin.readline().strip()

  if not bn.startswith('sample_input_part2_'):
    phases = 'sample_input_part1_0.txt'==bn and 4 or 100
    dt_part1_results = part1(s_lt_elements_0,phases)
    print(dict(part1=dt_part1_results))

  if not bn.startswith('sample_input_part1_'):
    phases = bn.startswith('sample_input_part2_') and 100 or 100
    dt_part2_results = part2(s_lt_elements_0,phases)
    print(dict(part2=dt_part2_results))
