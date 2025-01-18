"""
The utilities are for developers only.
  1. They are not accessible to users. 
  2. Should not be imported automatically.
  3. Should not appear in the doc.
"""

from typing import List
from typing import Dict
import pandas as pd
from itertools import zip_longest

# ------------------------------
# -   Feasible Bids and Asks   -
# ------------------------------
def feasible_bidask(M, clearing_price):
    """
    Given a clearing price, return the orderbook for users
    who are willing to buy/sell.

    Args:
        M (Market): a marekt instance

        clearning_price (float): the market clearing price
    
    Return:
        (Orderbook for buyers, Orderbook for sellers)
    """

    feasible_bids = M.book.orders[(M.book.orders["Type"] == "bid") & (M.book.orders["Price"] >= clearing_price)]
    feasible_asks = M.book.orders[(M.book.orders["Type"] == "ask") & (M.book.orders["Price"] <= clearing_price)]

    return feasible_bids, feasible_asks


# -------------------------------
# -   Proportional Allocation   -
# -------------------------------
def proportional_allocation(M, clearing_price, volume):
    """
    An allocation method (after clearing price is determined) based on 
    the proportion of bid/ask units of each participant.

    Source: Moulin, H. (2004). Fair division and collective welfare. MIT press.

    Args:
        M (Market): a marekt instance

        clearning_price (float): the market clearing price

        volume (int): the clearing volume

    Returns:
        None
        The two attributes: alloc_seller and alloc_buyer of M are updated to 
        record the resulting allocations.
    """

    # Extract the number of units for each buyer/seller if they 
    # have incentives to buy/sell under the clearing price
    feasible_bids, feasible_asks = feasible_bidask(M, clearing_price)

    # --- Compute the allocation ---

    # Step I: compute the total units for each user
    buyer_allocation = feasible_bids.groupby("User")["Unit"].sum().to_dict()
    seller_allocation = feasible_asks.groupby("User")["Unit"].sum().to_dict()

    # Step II: compute the total buying and selling units
    # Note: this total sum might not equal to the clearing volume,
    # as true clearing might not exist
    total_buy = sum(buyer_allocation.values())
    total_sell = sum(seller_allocation.values())

    # Step III: allocation based on the proportion
    for buyer in buyer_allocation.keys():
        active_vol = volume * (buyer_allocation[buyer] / total_buy) 
        new_row = pd.DataFrame({"User" : [buyer], "Units Bought" : [active_vol], "Price" : [clearing_price]})

        M.alloc_buyer = pd.concat([M.alloc_buyer, new_row], ignore_index=True)

    for seller in seller_allocation.keys():
        active_vol = volume * (seller_allocation[seller] / total_sell) 
        new_row = pd.DataFrame({"User" : [seller], "Units Sold" : [active_vol], "Price" : [clearing_price]})

        M.alloc_seller = pd.concat([M.alloc_seller, new_row], ignore_index=True)

# --------------------------
# -   Uniform Allocation   -
# --------------------------
def uniform_allocation(M, clearing_price, volume):
    """
    An allocation method (after clearing price is determined) with an
    even distribution of goods to among the participants.

    Source: Bogomolnaia, A., & Moulin, H. (2001). A new solution to the random assignment problem. Journal of Economic theory, 100(2), 295-328.

    Args:
        M (Market): a marekt instance
        clearning_price (float): the market clearing price
        volume (int): the clearing volume

    Returns:
        None
        The two attributes: alloc_seller and alloc_buyer of M are updated to 
        record the resulting allocations.
    """

    # Extract the number of units for each buyer/seller
    feasible_bids, feasible_asks = feasible_bidask(M, clearing_price)

    # --- Compute the allocation ---

    # Step I: compute the number of buyers and sellers
    buyer_num = feasible_bids["User"].nunique()
    seller_num = feasible_asks["User"].nunique()

    # Step II: evenly divide the overall units among the buyers and sellers
    for buyer in feasible_bids["User"]:
        active_vol = volume / buyer_num
        new_row = pd.DataFrame({"User" : [buyer], "Units Bought" : [active_vol], "Price" : [clearing_price]})
        M.alloc_buyer = pd.concat([M.alloc_buyer, new_row], ignore_index=True)

    for seller in feasible_asks["User"]:
        active_vol = volume / seller_num
        new_row = pd.DataFrame({"User" : [seller], "Units Sold" : [active_vol], "Price" : [clearing_price]})
        M.alloc_seller = pd.concat([M.alloc_seller, new_row], ignore_index=True)

# ------------------------------
# -   Price-Based Allocation   -
# ------------------------------
def price_priority_allocation(M, clearing_price, volume):
    """
    An allocation method (after clearing price is determined) using
    a ranking of users by the averged per-unit-price. 

    Source: Milgrom, P. (1989). Auctions and bidding: A primer. 
    Journal of economic perspectives, 3(3), 3-22.

    Args:
        M (Market): a marekt instance
        clearning_price (float): the market clearing price
        volume (int): the clearing volume

    Returns:
        None
        The two attributes: alloc_seller and alloc_buyer of M are updated to 
        record the resulting allocations.
    """

    # Extract the orderbook
    feasible_bids, feasible_asks = feasible_bidask(M, clearing_price)

    # --- Compute the allocation --- 

    # Step I: compute the averaged per-unit-price
    buyer_price_dict, seller_price_dict = {}, {}

    total_units_buyer = feasible_bids.groupby("User")["Unit"].sum().to_dict()
    total_units_seller = feasible_asks.groupby("User")["Unit"].sum().to_dict()

    for row in feasible_bids.itertuples(index=False):
        buyer = row.User
        units = row.Unit
        price = row.Price
        if buyer not in buyer_price_dict:
            buyer_price_dict[buyer] = price * units
        else:
            buyer_price_dict[buyer] += price * units

    for buyer in buyer_price_dict.keys(): 
        buyer_price_dict[buyer] /= total_units_buyer[buyer]
    
    for row in feasible_asks.itertuples(index=False):
        seller = row.User
        units = row.Unit
        price = row.Price
        if seller not in seller_price_dict:
            seller_price_dict[seller] = price * units
        else:
            seller_price_dict[seller] += price * units

    for seller in seller_price_dict.keys(): 
        seller_price_dict[seller] /= total_units_seller[seller]

    # Step II: ranking buyers and sellers by their per-unit-price
    # Note: Python 3.7+ supports ordered dict. Not using it here. 
    ordered_buyer = sorted(buyer_price_dict.keys(), 
                           key=lambda x: buyer_price_dict[x], reverse=True)
    ordered_seller = sorted(seller_price_dict.keys(), 
                            key=lambda x: seller_price_dict[x], reverse=True)

    # Step III: allocate the volumns untill zero based on the ordering
    buy_volume, sell_volume = volume, volume

    for buyer, seller in zip_longest(ordered_buyer, ordered_seller, fillvalue=None):
        if buyer != None and buy_volume != 0:
            vol = min(total_units_buyer[buyer], buy_volume)
            buy_volume = max(0, buy_volume - vol)

            new_row = pd.DataFrame({"User" : [buyer], "Units Bought" : [vol], "Price" : [clearing_price]})
            M.alloc_buyer = pd.concat([M.alloc_buyer, new_row], ignore_index=True)

        if seller != None and sell_volume != 0:
            vol = min(total_units_seller[seller], sell_volume)
            sell_volume = max(0, sell_volume - vol)

            new_row = pd.DataFrame({"User" : [seller], "Units Sold" : [vol], "Price" : [clearing_price]})
            M.alloc_seller = pd.concat([M.alloc_seller, new_row], ignore_index=True)
    
    # ---------------------------
    # -   Marginal Allocation   -
    # ---------------------------
    def marginal_allocation(M, clearing_price, volume):
        """
        Zirou: I am trying to figure out how this works.
        Allocate items to buyers and sellers on the margin of the supply and demand curves.
        """
        pass

# Factory
ALLOCATION_METHODS = {
    "proportional" : proportional_allocation,
    "uniform" : uniform_allocation,
    "price" : price_priority_allocation
}