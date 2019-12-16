import part1

for v12 in range(10000):
  v1 = v12 / 100
  v2 = v12 % 100
  if 19690720==part1.main('input.txt',v1=v1,v2=v2): print(v12)
