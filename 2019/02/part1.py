import os
import sys


def main(fn,v1=12,v2=2):
  with open(fn) as fin:
    lt_ints = list(map(int,fin.readline().strip().split(',')))
    lt_ints[1] = v1
    lt_ints[2] = v2
    for i in range(0,len(lt_ints),4):
      op,iin0,iin1,iout = [lt_ints[i+j] for j in range(4)]
      if 1==op:
        lt_ints[iout] = lt_ints[iin0] + lt_ints[iin1]
      elif 2==op:
        lt_ints[iout] = lt_ints[iin0] * lt_ints[iin1]
      elif 99==op:
        break
      else:
        assert dict()['{0},{1}'.format(i,op)]

  return lt_ints[0]

if "__main__"==__name__:
  print(main('input.txt'))
