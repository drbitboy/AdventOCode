import os
import sys
import eea   ### ../common/eea.py - Extended Euclidean Algorithm

do_debug = 'DEBUG' in os.environ

########################################################################
class DECK(list):
  """
  Model of a deck of cards, as a sub-class of the list type

  self.M:  Count of cards (defaults to DECK.Modulus)
  list(self):  original cards, from factory order, after shuffle(s)

  Factory order:  [0,1,2,...,self.M-1]

  """
  Modulus = 10007                       ### Default
  dins = 'deal into new stack'.split()  ### Tokens to deal new stack

  def __init__(self,narg=None):
    """Constructor:  set card count; create deck in factory order"""

    self.M = (narg is None) and DECK.Modulus or int(narg)
    self.clear()
    self.extend(range(self.M))


  def clear(self):
    """Remove items in list"""

    del self[0:]


  def cut(self,narg):
    """
    Split cards into two blocks; reverse those blocks' order; card order
    within each block does not change

    narg is integer (or string representing same) of spit location

    N.B. if int(narg) is positive, it is the split location offset
         from the start of the list i.e. the number of cards in the
         first block that that moved after the second block if int(narg)
         is negative, then it s the split location offset from the end
         of the list; this convention is the same as the list index
         convention in Python

    """

    n = int(narg)

    lt_new = self[n:] + self[:n]  ### Build list as cut of current list
    self.clear()                  ### Make current list empty
    self.extend(lt_new)           ### Add post-cut list to empty list

  def deal(self,narg=None):
    """
    Execute "deal into new stack" and "deal with increment <integer>"
    shuffles

    """
    if narg is None:
      ### "deal into new stack" reverses entire deck
      self.reverse()
    else:
      ### "deal with increment <integer>" moves card to location p into
      ### location (n * p) % M

      lt = tuple(self)              ### Copy list
      n = int(narg)                 ### Convert string or int to int
      for p in range(self.M):       ### Loop source postions
        self[(p*n)%self.M] = lt[p]  ### Move card at p to (p*n)

  def shuffles(self,fn):
    """Process multiple shuffles, each read as one line from a file"""

    with open(fn,'r') as fin:           ### Open file
      for rawline in fin:               ### Read on line in file
        toks = rawline.strip().split()  ### Break line into tokens

        if DECK.dins==toks:             ### deal into new stack
          self.deal()                   ### - execute

        elif toks[0]==DECK.dins[0]:     ### deal ...
          assert 'with'==toks[1]        ### ... with ...
          assert 'increment'==toks[2]   ### ... increment ...
          self.deal(toks[-1])           ### ... N; execute
        else:
          """cut <integer>"""
          assert 'cut'==toks[0]         ### cut ...
          self.cut(toks[-1])            ### ... N; execut3e

    return self


  def part1(self,n):
    """
    Part I solution:  find final location of card
                      from initial position n

    """

    return self,self.index(n%self.M)


########################################################################
class SHUFFLE(object):
  """Represent a shuffle technique, or series of same, as a linear,
modular equation.

For any shuffle technique, the card at position p will end up at
position p' = (self.a * p + self.b) % MODULUS

self.arev is integer that reverses self.a i.e.

  p = ((p' - self.b) * self.arev) $ MODULUS

"""

  def __init__(self,Marg=None):
    """Constructor:  start with factory order"""
    self.a,self.b = 1,0
    self.arev = 1
    self.M = Marg is None and DECK.Modulus or int(Marg)


  def cut(self,narg):
    """
    Implement [cut N] shuffle
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
    """Apply subsequent shuffle"""
    if isinstance(a_or_other,SHUFFLE):
      return self.apply(a_or_other=a_or_other.a,b=a_or_other.b)
    self.b = ((a_or_other * self.b) + b) % self.M
    self.a = (a_or_other * self.a) % self.M
    self.arev = None
    return self


  def square(self):
    """Multiply SHUFFLE by itself i.e. (a,b)**n becomes (a,b)**2n"""
    return self.apply(a_or_other=self)


  def shuffles(self,fn):
    """Process multiple shuffles, each read as one line from a file"""
    with open(fn,'r') as fin:
      for rawline in fin:

        toks = rawline.strip().split()

        if DECK.dins==toks:      ### Get (a,b) for "deal with new stack"
          a,b = self.deal()

        elif toks[0]==DECK.dins[0]:  ### Get (a,b) for "deal w/ incr. N"
          assert 4==len(toks)
          assert 'with'==toks[1]
          assert 'increment'==toks[2]
          a,b = self.deal(toks[-1])

        else:                        ### Get (a,b) for "cut N"
          assert 2==len(toks)
          assert 'cut'==toks[0]
          a,b = self.cut(toks[1])

        self.apply(a_or_other=a,b=b)   ### Apply shuffle via (a,b)

    return self


  def forward(self,ipos):
    """
    Apply forward shuffle of self to position ipos

    - Calculates final position of card at initial position ipos

    """
    return ((self.a * (ipos%self.M)) + self.b) % self.M


  def reverse(self,ipos):
    """
    Apply reverse shuffle of self to position ipos

    - Calculates intial position of card at final position ipos

    """

    ### Calculate Multiplicative Modulo Inverse using Extended Euclidean
    ### Algorithm (EEA) such that (self.a * self.arev) % M = 1

    if self.arev is None:
      ri,(si,self.arev,),iter = eea.eea(self.M,self.a)

    ### Apply reverse shuffle
    return (self.arev * ((ipos%self.M) - self.b)) % self.M


########################################################################
if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'


  ##################################
  ### Part I

  startpos = 2019

  ### Use DECK class to simulate factory-ordered deck shuffled per input file

  deck,part1 = DECK(narg=fn!='input.txt' and 10 or None).shuffles(fn).part1(startpos)
  if do_debug and 10==deck.M: print(list(deck))
  print(dict(n=deck.M,part1=part1))

  ### Use SHUFFLE class simulate the same thing as a check

  shuffle_part1 = SHUFFLE(Marg=deck.M).shuffles(fn)
  part1a=shuffle_part1.forward(startpos)
  print(dict(part1a=part1a))
  print(dict(it_should_be=startpos%shuffle_part1.M,it_is=shuffle_part1.reverse(part1a)))


  ##################################
  ### Part II

  M,Duplicates,endpos = 119315717514047,101741582076661,2020

  ### sh is initially a SHUFFLE instance simulating one pass through input file
  ### shuffle_part2 initially simualtes a factory-order deck i.e. no shuffle

  sh = SHUFFLE(Marg=M).shuffles(fn)
  shuffle_part2 = SHUFFLE(Marg=M)

  ### Number of passes through file; final shuffle will be sh**Duplicates

  Dups = Duplicates

  ### Step through numbers of passes in Dups using base-2 exponential
  ### steps i.e. loop over bits in Dups

  while Dups:

    ### If bit is present, multiply shuffle_part2 by current value of sh
    ### Square sh (sh**1 becomes sh**2, sh**4, sh**8, sh**16, etc.
    ### Shift bits of Dups one to the right

    if 1&Dups: shuffle_part2.apply(a_or_other=sh)
    sh.square()
    Dups >>= 1

  ### SHUFFLE instance shuffle_part2 now contains (a,b)**Duplicates,
  ### apply its reverse shuffle to end position

  print(dict(part2=shuffle_part2.reverse(endpos)))
