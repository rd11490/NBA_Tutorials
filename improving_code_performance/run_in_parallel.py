import multiprocessing as mp
import numpy as np
import datetime as dt


def multiply_by_y(x, y):
    # print out x so that we can see order of processing
    print(x)
    return x * y


if __name__ == '__main__':
    # Find out how many cores you have available
    print('Cores available: ', mp.cpu_count())

    # Build your pool
    pool = mp.Pool(mp.cpu_count())

    input_data = np.linspace(start=1, stop=20, num=20)
    print(input_data)
    results = []

    start_par = dt.datetime.now()
    for d in input_data:
        out = pool.apply_async(multiply_by_y, args=(d, 2))
        results.append(out)

    pool.close()
    pool.join()

    result = [r.get() for r in results]
    print('\n')
    print(result)




