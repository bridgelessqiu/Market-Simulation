import random
from typing import Dict
import pandas as pd
import warnings

# ----------------- 
#   First Price   -
# ----------------- 
def first_price_sealed_bid(M, bids : Dict):
    """Winners are those with the highest bids.

    Winners pay the highest bid.
    Ties are broken by an even distribution of the item.

    Args:
        M (Market):
            A one-sided market instance.
        bids (Dict):
            Contains the bids for each participants of the form:
            {user_id : price}
    Return:
        None
        The two attributes: alloc_seller and alloc_buyer of M are updated to 
        record the resulting allocations.
    """

    winning_bid = max(bids.values())  # As in the first price auction.
    winners = [u for u, bid in bids.items() if bid == winning_bid]

    rows = []
    for u in winners:
        new_row = {"User" : u, "Units Bought" : 1/len(winners), "Price" : winning_bid * 1/len(winners)}
        rows.append(new_row)

    M.alloc_buyer = pd.DataFrame(rows)

# ----------------- 
#   Second Price  -
# ----------------- 
def second_price_sealed_bid(M, bids : Dict):
    """Winners are those with the highest bids.

    Winners pay the second highest bid.
    Ties are broken by an even distribution of the item.

    Args:
        M (Market):
            A one-sided market instance.
        bids (Dict):
            Contains the bids for each participants of the form:
            {user_id : price}
    Return:
        None
        The two attributes: alloc_seller and alloc_buyer of M are updated to 
        record the resulting allocations.
    """

    # Find the largest and the second largest bid.
    max_bid, sec_bid = -1, -1
    for bid in bids.values():
        if bid >= max_bid:
            max_bid = bid 
        elif bid > sec_bid:
            sec_bid = bid

    winners = [u for u, bid in bids.items() if bid == max_bid]

    rows = []
    for u in winners:
        new_row = {"User" : u, "Units Bought" : 1/len(winners), "Price" : sec_bid * 1/len(winners)}
        rows.append(new_row)

    M.alloc_buyer = pd.DataFrame(rows)

# -------------------- 
#   Double Auction   -
# -------------------- 
def double_auction(M, bids : Dict):
    warnings.warn("For double auctions, please use the pooled market class.")

# --------------------- 
#   Reverse Auction   -  
# --------------------- 
def reverse_auction(M, bids : Dict):
    """Winners are those with the lowest bids.

    Winners pay the lowest bid.
    Ties are broken by an even distribution of the item.

    Args:
        M (Market):
            A one-sided market instance.
        bids (Dict):
            Contains the bids for each participants of the form:
            {user_id : price}
    Return:
        None
        The two attributes: alloc_seller and alloc_buyer of M are updated to 
        record the resulting allocations.
    """
    winning_bid = min(bids.values())  # As in the reverse auction.
    winners = [u for u, bid in bids.items() if bid == winning_bid]

    rows = []
    for u in winners:
        new_row = {"User" : u, "Units Bought" : 1/len(winners), "Price" : winning_bid * 1/len(winners)}
        rows.append(new_row)

    M.alloc_buyer = pd.DataFrame(rows)


AUCTION_METHODS = {
    "first_price" : first_price_sealed_bid,
    "second_price": second_price_sealed_bid,
    "double": double_auction,
    "reverse": reverse_auction
}

# "english": english_auction,
# "dutch": dutch_auction,
# "all_pay": all_pay_auction,