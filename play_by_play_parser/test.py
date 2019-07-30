lst = [1, 2, 3, 4, 5, 6, 7]

for ind, i in enumerate(lst):
    print(i)
    subset = lst[ind+1: min(ind+3, len(lst))]
    subset.reverse()
    print(subset)
    print('NEXT')


