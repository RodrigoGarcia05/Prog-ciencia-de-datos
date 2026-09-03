def myfunc(n): 
      return abs(n - 50) 

thislist = [100, 50, 65, 82, 23] 
largo= len(thislist)

for i in range(largo):
    for j in range( 0, largo - i - 1):
        if myfunc(thislist[j]) > myfunc(thislist[j + 1 ]):
            thislist[j], thislist[j + 1] = thislist[j +1], thislist[j]
            
print(thislist) 
