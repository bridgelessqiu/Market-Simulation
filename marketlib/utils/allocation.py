""" Allocation methods for market clearing.

    Allocation happens after a clearing price is computed.
"""

import pandas as pd
from itertools import zip_longest

# ------------------------------
# -   Feasible Bids and Asks   -
# ------------------------------
def feasible_bidask(M, clearing_price : float):
    """ Given a clearing price, find users who are willing to buy or sell.

    Args:
        M (Market): 
            A market instance.
        clearning_price (float): 
            The market clearing price.
    
    Return:
        A tuple of the form: (Orderbook for feasible buyers, Orderbook for feasible sellers).
    """

    feasible_bids = M.book.orders[(M.book.orders["Type"] == "bid") & (M.book.orders["Price"] >= clearing_price)]
    feasible_asks = M.book.orders[(M.book.orders["Type"] == "ask") & (M.book.orders["Price"] <= clearing_price)]

    return feasible_bids, feasible_asks

# -------------------------------
# -   Proportional Allocation   -
# -------------------------------
def proportional_allocation(M, clearing_price, volume):
    """ Allocate based on the proportion of bid/ask units of each participant.
    
    Consider the buyer side. The seller's allocation happens analogously. For a
    Buyer i, let U_i denote the number of units that i is willing to trade under clearing price p. Let U denote the total number of feasible units over all the buyers under p. Note that, in the case of a shortage, U is greater than the clearing volume. 
    The number of units that i receives equals to clearing_volume * (U_i / U).
    
    Source: Moulin, H. (2004). Fair division and collective welfare. MIT press.

    Args:
        M (Market): 
            A market instance.
        clearning_price (float): 
            The market clearing price.
        volume (int): 
            The clearing volume.

    Returns: 
        None. The two attributes: alloc_seller and alloc_buyer of M are updated to record the resulting allocations.
    """

    # Extract the number of feasible units for each buyer/seller if they 
    # have incentives to buy/sell under the clearing price.
    feasible_bids, feasible_asks = feasible_bidask(M, clearing_price)

    # Step I: Compute the total units for each user that is willing to trade.
    buyer_allocation = feasible_bids.groupby("User")["Unit"].sum().to_dict()
    seller_allocation = feasible_asks.groupby("User")["Unit"].sum().to_dict()

    # Step II: compute the total feasible bid and ask units.
    # This total sum might not equal to the clearing volume, as true
    # clearing might not exist.
    total_buy = sum(buyer_allocation.values())
    total_sell = sum(seller_allocation.values())

    # Step III: allocation.
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
    """ Even distribution of goods to among the participants.
    
    For the set of feasible buyers / sellers, each participants receives the same number of units from the total clearing volume.

    Source: Bogomolnaia, A., & Moulin, H. (2001). A new solution to the random assignment problem. Journal of Economic theory, 100(2), 295-328.

    Args:
        M (Market): 
            A market instance.
        clearning_price (float): 
            The market clearing price.
        volume (int): 
            The clearing volume.

    Returns:
        None. The two attributes: alloc_seller and alloc_buyer of M are updated to record the resulting allocations.
    """

    # Extract the number of units for each buyer/seller.
    feasible_bids, feasible_asks = feasible_bidask(M, clearing_price)

    # Step I: Compute the number of buyers/sellers that are willing to trade.
    buyer_num = feasible_bids["User"].nunique()
    seller_num = feasible_asks["User"].nunique()

    # Step II: Evenly divide the clearing units.
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
    """ Rank users by the averaged per-unit price, then allocate.

    Let i be a buyer that is willing to trade under the clearing price. Let alpha_i denote the per-unit price of i, computed over all feasible bids of i. The market ranks all buyers (who are willing to trade) based on its per-unit price alpha_i in non-ascending order. Then, the market tries to satisfies the units desired for each buyer following this priority list, until all clearing units are distributed. The allocation for sellers happens analogously, excepts that they are ranked in non-descending order.

    Source: Milgrom, P. (1989). Auctions and bidding: A primer. 
    Journal of economic perspectives, 3(3), 3-22.

    Args:
        M (Market): 
            A market instance.
        clearing_price (float): 
            The market clearing price.
        volume (int): 
            The clearing volume.

    Returns:
        None. The two attributes: alloc_seller and alloc_buyer of M are updated to record the resulting allocations.
    """

    feasible_bids, feasible_asks = feasible_bidask(M, clearing_price)

    # Step I: Compute the averaged per-unit price.
    # buyer_price_dict = {buyer : per-unit price}
    buyer_price_dict, seller_price_dict = {}, {}

    # total_units_buyer = {buyer : units}
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

    # Step II: Ranking buyers and sellers by their per-unit-price.
    # Python 3.7+ supports ordered dict. Not using it here. 
    ordered_buyer = sorted(buyer_price_dict.keys(), 
                           key=lambda x: buyer_price_dict[x], reverse=True)
    
    # Sellers are ranked in non-descending order.

    ordered_seller = sorted(seller_price_dict.keys(), 
                            key=lambda x: seller_price_dict[x])

    # Step III: Allocate the volumes based on the ordering.
    buy_volume, sell_volume = volume, volume

    for buyer, seller in zip_longest(ordered_buyer, ordered_seller, fillvalue=None):
        if buyer is not None and buy_volume != 0:
            vol = min(total_units_buyer[buyer], buy_volume)
            buy_volume = max(0, buy_volume - vol)

            new_row = pd.DataFrame({"User" : [buyer], "Units Bought" : [vol], "Price" : [clearing_price]})
            M.alloc_buyer = pd.concat([M.alloc_buyer, new_row], ignore_index=True)

        if seller is not None and sell_volume != 0:
            vol = min(total_units_seller[seller], sell_volume)
            sell_volume = max(0, sell_volume - vol)

            new_row = pd.DataFrame({"User" : [seller], "Units Sold" : [vol], "Price" : [clearing_price]})
            M.alloc_seller = pd.concat([M.alloc_seller, new_row], ignore_index=True)
    
# ------------------------------
# -   Max-Welfare Allocation   -
# ------------------------------
def welfare_allocation(M, clearing_price, volume):
    """ Allocation that maximizes the welfare. 

    The utility of each participant i is computed as follows:
    "valuation of the units allocated - the actual payment".

    An example:
        A buyer i submits two bids:
        1. $5 per unit for the first 10 units
        2. $2 per unit for the next 5 units

        Under a clearing price of $1, and 12 units allocated to i, 
        its utility would be:
            (5 * 10 + 2 * 2) - 12 * 1
        or in a per-unit expression:
            (5 - 1) * 10 + (2 - 1) * 2
    
    Args:
        M (Market): 
            A market instance.
        clearning_price (float): 
            The market clearing price.
        volume (int): 
            The clearing volume.

    Returns:
        None. The two attributes: alloc_seller and alloc_buyer of M are updated to record the resulting allocations.
    """

    feasible_bids, feasible_asks = feasible_bidask(M, clearing_price)

    # Step I: Sort the bids (non-ascending) and asks (non-descending) by price.
    # Note that we sort bids and asks, not participants.
    feasible_bids = feasible_bids.sort_values(by="Price", ascending=False)
    feasible_asks = feasible_asks.sort_values(by="Price", ascending=True)

    # Step II: allocation by prices
    buy_welfare, sell_welfare = 0, 0  # Nice to keep track
    buy_vol, sell_vol = volume, volume

    for row in feasible_bids.itertuples(index=False):
        if buy_vol == 0:  # When all volumes are allocated
            break
        buyer = row.User
        units = row.Unit
        price = row.Price

        actual_units = min(buy_vol, units)
        buy_vol = max(0, buy_vol - actual_units)
        buy_welfare += (price - clearing_price) * actual_units

        new_row = pd.DataFrame({"User" : [buyer], "Units Bought" : [actual_units], "Price" : [clearing_price]})
        M.alloc_buyer = pd.concat([M.alloc_buyer, new_row], ignore_index=True)

    M.alloc_buyer = M.alloc_buyer.groupby("User", as_index=False).agg({"Units Bought": "sum", "Price": "first"})

    for row in feasible_asks.itertuples(index=False):
        if sell_vol == 0:
            break
        seller = row.User
        units = row.Unit
        price = row.Price

        actual_units = min(sell_vol, units)
        sell_vol = max(0, sell_vol - actual_units)
        sell_welfare += (price - clearing_price) * actual_units

        new_row = pd.DataFrame({"User" : [seller], "Units Sold" : [actual_units], "Price" : [clearing_price]})
        M.alloc_seller = pd.concat([M.alloc_seller, new_row], ignore_index=True)

    M.alloc_seller = M.alloc_seller.groupby("User", as_index=False).agg({"Units Sold": "sum", "Price": "first"})

# Factory
ALLOCATION_METHODS = {
    "proportional" : proportional_allocation,
    "uniform" : uniform_allocation,
    "price" : price_priority_allocation,
    "welfare" : welfare_allocation
}