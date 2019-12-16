import os
import sys

sum = 0

for rawline in sys.stdin:

  val = int(rawline.strip())
  while val > 8:
    val = ((val - (val%3)) / 3) - 2
    sum += val

print(sum)
