"""
Extended Euclidean Algorithm for finding Modular Multiplicative Inverse
""".strip()

import os

do_debug = 'EEA_DEBUG' in os.environ

def eea(m,a):
  """
Extended Euclidean Algorithm for finding Modular Multiplicative Inverse

Arguments are integers, with m > a

Returns tuple:  (GCD(m,a), (x,y), I)

- GCD:  Greatest Common
- (x,y):  such that mx + by = GCD(m,a)
- I:  final value of i

"""
  assert m>a

  ### Suffixes:  ip1 => i+1; im1 => i-1

  ### Initialize:  ri = m; r(i+1) = a; 

  ri,rip1 = m,a
  tip1,ti = si,sip1 = 1, 0
  i = 1

  while rip1 > 0:

    ri,rim1,si,sim1,ti,tim1,i =  rip1,ri,sip1,si,tip1,ti,i+1

    rip1 = rim1 % ri
    qi = (rim1-rip1) / ri
    sip1 = sim1 - (qi * si)
    tip1 = tim1 - (qi * ti)

  assert rim1 == ((m * sim1) + (a * tim1))

  if do_debug: print((m,a,ri,(si,ti,),i,))

  return ri,(si,ti,),i


def test_eea():
  assert eea(7,2)[:2] == (1,(1,-3,),)
  assert eea(7,3)[:2] == (1,(1,-2,),)
  assert eea(11,2)[:2] == (1,(1,-5),)
  assert eea(11,3)[:2] == (1,(-1,4,),)


if "__main__" == __name__:
  test_eea()
