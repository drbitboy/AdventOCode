import os
import sys

class ORBITS(dict):
  def __init__(self,fn):
    super(ORBITS,self).__init__(self)
    with open(fn,'r') as fin:
      for rawline in fin:
        center,orbiter = rawline.strip().split(')')
        assert (not (orbiter in self)) or dict()[rawline]
        self[orbiter] = center

  def part1(self):
    sum = 0
    for key in self.keys():
      while key in self:
        sum += 1
        key = self[key]
      assert 'COM'==key
    return sum

  def centers(self,orbiter):
    lt = [orbiter]
    while orbiter in self:
      orbiter = self[orbiter]
      lt.append(orbiter)
    return lt

  def part2(self,you='YOU',santa='SAN'):
    lt_you = self.centers(you)
    lt_santa = self.centers(santa)
    while lt_you and lt_santa:
      ctr_you,ctr_santa = lt_you.pop(),lt_santa.pop()
      if ctr_you != ctr_santa: break
      print((lt_you[-2:],lt_santa[-2:],))

    return len(lt_you + lt_santa),len(lt_you),len(lt_santa)
    

if "__main__" == __name__:
  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  orbits = ORBITS(fn)
  print(orbits.part1())
  print(orbits.part2())
