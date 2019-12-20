import os
import sys
import pickle

if "__main__" == __name__:
  fn = sys.argv[1:] and sys.argv[1] or '15.pickle'
  with open(fn,'rb') as fin:
    results = pickle.load(fin)

  for k in results:

    visited,blocked,found2=results[k]
    all=visited.union(blocked)

    print(dict(len_all=len(all),len_visited=len(visited),len_blocked=len(blocked)))
    print(visited.intersection(blocked))
    assert len(all)==(len(visited)+len(blocked))
    def minmax(xys): return min(xys),max(xys)
    (xmin,xmax,),(ymin,ymax,) = minmax = map(minmax,zip(*(all))[:2])

    dt={0:'.',9:'*',1:' ',2:'@'}
    nx,ny = 1 + xmax - xmin,1 + ymax - ymin
    ltlt = [[' ']*nx for i in range(ny)]
    for x,y in visited: ltlt[y-ymin][x-xmin] = (x or y) and ' ' or 'O'
    for x,y in blocked: ltlt[y-ymin][x-xmin] = '.'
    ltlt[found2[1]-ymin][found2[0]-xmin] = 'X'

    print('\n'.join([''.join(lt) for lt in ltlt]))
    print(dict(name=k,minmax=minmax,nx=nx,ny=ny))

