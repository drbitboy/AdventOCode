import os
import sys

if "__main__" == __name__:
  twos,threes = 0,0
  st_25 = set()
  st_ans = set()
  for word in sys.stdin:
    word = word.strip()
    lt = list(' '+word)
    lt.sort()
    letter = ''
    ct = 0
    st = set()
    while lt:
      last = letter
      letter = lt.pop()
      if letter == last:
        ct += 1
      else:
        st.add(ct)
        ct = 1
    if 2 in st: twos += 1
    if 3 in st: threes += 1
    lt_w25s = [word[:i]+word[i+1:] for i in range(len(word)-2)]
    for w25 in lt_w25s:
      if w25 in st_25: st_ans.add(w25)
    list(map(st_25.add,lt_w25s))
  print(twos*threes)
  print(st_ans)
