import sys

if "__main__" == __name__:
  pairs = sum([[s.upper()+s,s+s.upper()]
               for s in 'abcdefghijklmnopqrstuvwxyz'
              ],[])

  s = sys.stdin.read(50010).strip()

  L = len(s) + 10

  while len(s) < L:
    L = len(s)
    for pair in pairs: s = s.replace(pair,'')

  print(len(s))
