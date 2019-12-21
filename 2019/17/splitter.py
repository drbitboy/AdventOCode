import os

cmma = ','

do_debug = 'DEBUG' in os.environ

def splitter17(s_original):

  if do_debug: print(dict(s_original=s_original))

  A = s_original[:21]
  if 21>len(A): A = '{0},'.format(A)

  while True:

    ### Code will crash here on failure i.e. if split can't be done

    while cmma!=A[-1]: A = A[:-1]
    A = A[:-1]

    if A[-1] in 'LR':
      while cmma!=A[-1]: A = A[:-1]
      A = A[:-1]

    lt1 = [s.strip(cmma) for s in s_original.split(A) if s.strip(cmma)]
    if do_debug: print(dict(A=A,lt1=lt1))

    if not lt1: return dict(A=A,B=A,C=A)

    B = '{0},'.format(lt1[0][:20])
    while True:

      while B and cmma!=B[-1]: B = B[:-1]
      if not B: break
      assert cmma==B[-1]
      B = B[:-1]

      if B[-1] in 'LR':
        while B and cmma!=B[-1]: B = B[:-1]
        if not B: break
        assert cmma==B[-1]
        B = B[:-1]

      if do_debug: print(dict(B=B))

      lt2 = sum([[s.strip(cmma) for s in s1.split(B) if s.strip(cmma)]
                 for s1 in lt1
                ]
                ,[]
                )

      if not lt2: return dict(A=A,B=B,C=B)

      st2 = set(lt2)
      if do_debug: print(dict(st2=st2))
      if 1<len(st2): continue
      C = lt2.pop()
      if 21>len(C): return dict(A=A,B=B,C=C)


if "__main__" == __name__:

  full_result = {'part2': {'A': 'R,6,L,10,R,8,R,8', 'Loutputs': 6465, 'B': 'R,12,L,8,L,10', 'main_routine': 'A,B,A,C,B,C,A,B,A,C', 'C': 'R,12,L,10,R,6,L,10', 's_commands': 'R,6,L,10,R,8,R,8,R,12,L,8,L,10,R,6,L,10,R,8,R,8,R,12,L,10,R,6,L,10,R,12,L,8,L,10,R,12,L,10,R,6,L,10,R,6,L,10,R,8,R,8,R,12,L,8,L,10,R,6,L,10,R,8,R,8,R,12,L,10,R,6,L,10', 'lt_result': [1168948]}}

  splitter_result = splitter17(full_result['part2']['s_commands'])

  assert set([splitter_result[s] for s in 'ABC']
            )==set([full_result['part2'][s] for s in 'ABC'])

  print(splitter_result)

  print(splitter17('R,8,R,12'))
  print(splitter17('R,8,R,12,L,4,L,8,L,21,R,8,R,12,L,21,R,8,R,12,L,21,R,8,R,12'))
