"""
The utilities are for developers only.
  1. They are not accessible to users. 
  2. Should not be imported automatically.
  3. Should not appear in the doc.
"""

from typing import List
from typing import Dict
import pandas as pd

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
    feasible_bids = M.book.orders[(M.book.orders["Type"] == "bid") & (M.book.orders["Price"] >= clearing_price)]
    feasible_asks = M.book.orders[(M.book.orders["Type"] == "ask") & (M.book.orders["Price"] <= clearing_price)]

    # --- Compute the actual allocation ---
    buyer_allocation = feasible_bids.groupby("User")["Unit"].sum().to_dict()
    seller_allocation = feasible_asks.groupby("User")["Unit"].sum().to_dict()


    # Note: this total sum might not equal to the clearing volume,
    # as true clearing might not exist
    total_buy = sum(buyer_allocation.values())
    total_sell = sum(seller_allocation.values())

    for buyer in buyer_allocation.keys():
        active_vol = volume * (buyer_allocation[buyer] / total_buy) 
        new_row = pd.DataFrame({"User" : [buyer], "Units Bought" : [active_vol], "Price" : [clearing_price]})

        M.alloc_buyer = pd.concat([M.alloc_buyer, new_row], ignore_index=True)

    for seller in seller_allocation.keys():
        active_vol = volume * (seller_allocation[seller] / total_sell) 
        new_row = pd.DataFrame({"User" : [seller], "Units Sold" : [active_vol], "Price" : [clearing_price]})

        M.alloc_seller = pd.concat([M.alloc_seller, new_row], ignore_index=True)

# Factory
ALLOCATION_METHODS = {
    "proportional" : proportional_allocation
}