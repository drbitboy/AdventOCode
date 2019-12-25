import os
import sys
import eea


########################################################################
class DECK(list):
  Modulus = 10007
  Range = range(Modulus)
  dins = 'deal into new stack'.split()

  def __init__(self,narg=None):
    self.clear()
    if narg is None:
      self.n = DECK.Modulus
      self.range = DECK.Range
      self.extend(DECK.Range)
    else:
      self.n = int(narg)
      self.range = range(self.n)
      self.extend(self.range)

  def clear(self): del self[0:]

  def cut(self,narg):
    n = int(narg)
    lt_new = self[n:] + self[:n]
    self.clear()
    self.extend(lt_new)

  def deal(self,narg=None):
    if narg is None:  self.reverse()
    else:
      lt = tuple(self)
      n = int(narg)
      for i in range(0,self.n*n,n):
        self[i%self.n] = lt[i/n]

  def shuffles(self,fn):
    """Process multiple shuffles, each read as one line from a file"""
    with open(fn,'r') as fin:
      for rawline in fin:
        toks = rawline.strip().split()
        if DECK.dins==toks:
          """deal into new stack"""
          self.deal()
        elif toks[0]==DECK.dins[0]:    ### deal
          """deal with increment <integer>"""
          assert 'with'==toks[1]
          assert 'increment'==toks[2]
          self.deal(toks[-1])
        else:
          """cut <integer>"""
          self.cut(toks[-1])

    return self

  def linear(self,shuffle):
    """Process a shuffle using a SHUFFLE object (below)"""

  def part1(self,n):
    return self,self.index(n%self.n)


########################################################################
class SHUFFLE(object):
  """Represent a shuffle technique, or series of same, as a linear,
modular equation.

For any shuffle technique, the card at position p will end up at
position p' = (ap + b) % MODULUS

"""

  def __init__(self,Marg=None):
    self.a,self.b = 1,0
    self.arev = 1
    self.M = Marg is None and DECK.Modulus or int(Marg)


  def cut(self,narg):
    """
    narg==2:  012345 => 234501
    narg==-2:  012345 => 450123
    p' = -narg + 1p   with narg>0

    """
    n = int(narg)
    if n < 0: n = self.M + n
    return 1,-n


  def deal(self,narg=None):
    """deal into new stack, or deal with increment <integer>"""
    if narg is None: return -1, self.M - 1
    else           : return int(narg), 0


  def apply(self,a_or_other=None,b=None):
    if isinstance(a_or_other,SHUFFLE):
      return self.apply(a_or_other=a_or_other.a,b=a_or_other.b)
    self.b = ((a_or_other * self.b) + b) % self.M
    self.a = (a_or_other * self.a) % self.M
    self.arev = None
    return self


  def square(self):
    return self.apply(a_or_other=self)


  def shuffles(self,fn):
    """Process multiple shuffles, each read as one line from a file"""
    with open(fn,'r') as fin:
      for rawline in fin:

        toks = rawline.strip().split()

        if DECK.dins==toks:
          """deal into new stack"""
          a,b = self.deal()

        elif toks[0]==DECK.dins[0]:            ### deal
          """deal with increment <integer>"""
          assert 4==len(toks)
          assert 'with'==toks[1]
          assert 'increment'==toks[2]
          a,b = self.deal(toks[-1])
        else:
          """cut <integer>"""
          assert 2==len(toks)
          assert 'cut'==toks[0]
          a,b = self.cut(toks[1])

        self.apply(a_or_other=a,b=b)

    return self


  def forward(self,ipos):
    return ((self.a * (ipos%self.M)) + self.b) % self.M


  def reverse(self,ipos):
    if self.arev is None:
      ri,(si,self.arev,),iter = eea.eea(self.M,self.a)
    return (self.arev * ((ipos%self.M) - self.b)) % self.M


########################################################################
if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'

  ### Part II

  startpos = 2019

  deck,part1 = DECK(narg=fn!='input.txt' and 10 or None).shuffles(fn).part1(startpos)
  if 10==deck.n: print(list(deck))
  print(dict(n=deck.n,part1=part1))

  shuffle_part1 = SHUFFLE(Marg=deck.n).shuffles(fn)
  part1a=shuffle_part1.forward(startpos)
  print(dict(part1a=part1a))
  print(dict(it_should_be=startpos%shuffle_part1.M,it_is=shuffle_part1.reverse(part1a)))

  ### Part II

  M,Duplicates,endpos = 119315717514047,101741582076661,2020

  sh = SHUFFLE(Marg=M).shuffles(fn)
  shuffle_part2 = SHUFFLE(Marg=M)

  Dups = Duplicates

  while Dups:
    if 1&Dups: shuffle_part2.apply(a_or_other=sh)
    sh.square()
    Dups >>= 1

  print(dict(part2=shuffle_part2.reverse(endpos)))
