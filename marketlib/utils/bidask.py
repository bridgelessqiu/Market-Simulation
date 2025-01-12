"""
The utilities are for developers only.
  1. These are not accessible to users. 
  2. Should not be imported automatically.
  3. Should not appear in the doc.
"""

from typing import List
from typing import Dict

# ----------------------
# -   Cumulative Sum   -
# ----------------------
def cumu_sum(units : List):
    """
    Calculates the cumulative sum of a sequence of numbers (units), 
    yields the result incrementally

    Args:
        units (list): list of (supply/demand) units.

    Returns:
        A generator object
    """
    total = 0

    for u in units:
        total += u
        yield total

# --------------------------
# -   Find Cap Bid Price   -
# --------------------------
def search_bid(p : float, bid_prices : List):
    """
    Find the smallest bid prices that is at least p.
    This function is used in simple market clearing.

    Args:
        p (float): A clearing price.

        bid_price (list): A list of bid prices.
            warning: This list should be sorted in 
            non-ascending order.
        
    Returns:
        float: the smallest bid prices that is at least p.
    """

    n = len(bid_prices)

    # Check if the prices are sorted in non-ascending order
    if not all(bid_prices[i] >= bid_prices[i+1] for i in range(n - 1)):
        bid_prices = sorted(bid_prices, reverse=True)

    # Binary Search
    left, right = 0, n-1

    while left < right:
        mid = (left + right) // 2
        if bid_prices[mid] >= p:
            left = mid + 1
        else:
            right = mid

    # Check corner cases
    if bid_prices[left] >= p:
        return bid_prices[left]
    else:
        if left == 0:
            return -1
        else:
            return bid_prices[left - 1]


# --------------------------
# -   Find Cap Ask Price   -
# --------------------------
def search_ask(p : float, ask_prices : list):
    """
    Find the largest ask prices that is at most p.
    This function is used in simple market clearing.

    Args:
        p (float): A clearing price.

        ask_price (list): A list of ask prices.
            warning: This list should be sorted in 
            non-descending order.
        
    Returns:
        float: the largest ask prices that is at most p.
    """

    n = len(ask_prices)

    # Check if the prices are sorted in non-descending order
    if not all(ask_prices[i] <= ask_prices[i+1] for i in range(n - 1)):
        ask_prices = sorted(ask_prices)

    # Binary search
    left, right = 0, n-1

    while left < right:
        mid = (left + right) // 2
        if ask_prices[mid] <= p:
            left = mid + 1
        else:
            right = mid

    # Check corner cases
    if ask_prices[left] <= p:
        return ask_prices[left]
    else:
        if left == 0:
            return -1
        else:
            return ask_prices[left - 1]


# ---------------------------------
# -   Computing clearing volumn   -
# ---------------------------------
def compute_vol(p : float, cumu_bids : Dict, cumu_asks : Dict):
    """
    Compute the trade volumn under price p.

    Args:
        p (float): a clearing price.

        cumu_bids (dict): A dict of the form: [price, cumulative bid volumns upto this price] 

        cumu_asks (dict): A dict of the form: [price, cumulative ask volumns upto this price] 

    Returns:
        2-tuple: (clearing volumn, gap)

    """

    # Get ready for binary search
    bid_prices = sorted(cumu_bids.keys(), reverse=True)
    ask_prices = sorted(cumu_asks.keys())

    # Binary search, find the feasible bid and ask volumns
    bid_vol = cumu_bids[search_bid(p, bid_prices)]
    ask_vol = cumu_asks[search_ask(p, ask_prices)]

    vol, gap = min(bid_vol, ask_vol), abs(bid_vol - ask_vol)

    return vol, gap