import sys

if "__main__" == __name__:

  ### build ['Aa','aA','Bb',...,'zZ']

  pairs = sum([[s.upper()+s,s+s.upper()]
               for s in 'abcdefghijklmnopqrstuvwxyz'
              ],[])

  s = sys.stdin.read(50010).strip()

  ### remove [replace] string from s
  rrsfs = lambda input_string,remme:input_string.replace(remme,'')


  def partI(s):
    """Find shortest length after recursively removing all pairs"""
    L = len(s) + 10

    while len(s) < L:
      L = len(s)
      for pair in pairs: s = s.replace(pair,'')
    return L

  print(partI(s))

  def partII(s):
    return min(map(partI,[rrsfs(rrsfs(s,d[0]),d[1]) for d in pairs]))

  print partII(s)
