import os
import sys

layer_count = lambda str_layer,c: len([None
                                       for cl in str_layer
                                       if cl==c
                                      ])

########################################################################
def part1(str_layer):
  n0 = layer_count(str_layer,'0')
  n1 = layer_count(str_layer,'1')
  n2 = layer_count(str_layer,'2')
  return n0,n1*n2
########################################################################

########################################################################
def part2(str_layer):
  pixels = list(map(lambda lt:''.join(lt).replace('2','')[0],zip(*str_layer)))
  img_data = ''.join(pixels).replace('1','@').replace('0',' ')
  return '\n'.join([img_data[i:i+w] for i in range(0,area,w)])
########################################################################


w,h = 25,6
area = w * h

if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'

  with open(fn,'r') as fin:
    str_rawdata = fin.read().replace('\n','')
  L = len(str_rawdata)

  lt_layers = [str_layer
               for str_layer in [str_rawdata[i:i+area]
                                 for i in range(0,L,area)
                                ]
               if area==len(str_layer)
              ]

  print(sorted(map(part1,lt_layers))[0])
  print(part2(lt_layers))
