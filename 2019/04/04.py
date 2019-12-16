import os
import sys

def pwd_test(val):
  if val < 100000: return False
  if val > 999999: return False
  digit = 10
  duplicated = 1
  min_duplicated = 7
  no_decrease = True

  while val > 0:

    lastdigit = digit
    digit = val % 10
    val = (val - digit) / 10

    if digit == lastdigit:
      duplicated += 1
      if val > 0: continue

    if duplicated > 1 and min_duplicated > duplicated:
      min_duplicated = duplicated
    duplicated = 1
    if digit>lastdigit: no_decrease = False

  return val,min_duplicated,no_decrease

class PWDS(object):

  def __init__(self,fn):

    with open(fn,'r') as fin:
      self.flo,self.fhi = map(int,fin.read().strip().split('-'))

    self.pwds = list(map(pwd_test,range(self.flo,self.fhi+1)))

  def part1(self,duplim=7):
    return len([val
                for val,min_dup,no_decrease in self.pwds
                if no_decrease and (min_dup<duplim)
               ]
              )

  def part2(self):
    return self.part1(duplim=3)

if "__main__" == __name__:
  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  pwds = PWDS(fn)
  print(pwds.part1())
  print(pwds.part2())
