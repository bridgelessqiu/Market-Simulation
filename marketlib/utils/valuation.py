import random

def is_seller(rank : int, N : int, delta : float):
    return (rank / N >= 1 - delta)

def compute_valuation(beta : float, k1: int, k2: int, type: str):
    valuation = {}
    part = [k1, k2]

    # Note that we are doing something different from Abhijin's paper
    # Here, instead of compute a unique price for each unit of water,
    # we partition the k units into two subsets, with size k1 and k2.
    # Then, the prices of the water in the first set (of size k1) is 
    # of the same, computed using the formula with \ell = k1. Analogously 
    # the second set with k2 units. 

    if type == "seller":
        for i, a in enumerate(part):
            price = round(beta * a, 10)
            valuation[i] = (a, price)
    else:
        for i, a in enumerate(part):
            price = round(beta * ((k1 + k2) - a + 1), 10)
            valuation[i] = (a, price)

    return valuation

def is_high_value(lamb : float, i : int, N : int):
    """
    Returns True with probability:
        lamb * i / N + (1 - lamb) * (1 - i / N)
    """

    p = lamb * (i / N) + (1 - lamb) * (1 - i / N)
    return random.random() < p