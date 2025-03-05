from collections import defaultdict
import pandas as pd

def middle_bargaining(M, matching):
    """
    Meet-in-the-middle bargaining method. Given a pair of matched
    participants, a buyer A and a seller B. Under this mechanism,
    the agree price equals to the arithmetic mean of the bidding price
    and the asking price. 

    Args:
        M (Market): 
            The market where bargaining happens.

        matching (dict): 
            The buyer-seller matching returned by a matching mechanism.
    
    Returns:
        None
        The two attributes: alloc_seller and alloc_buyer of M are updated to 
        record the resulting allocations.
    """

    bids = M.book.orders[(M.book.orders["Type"] == "bid")]
    asks = M.book.orders[(M.book.orders["Type"] == "ask")]

    # Format: {user_id : [(price, units) ...]}
    buyer_price_dict, seller_price_dict = defaultdict(list), defaultdict(list)

    for row in bids.itertuples(index=False):
        user = row.User
        price = row.Price
        units = row.Unit

        buyer_price_dict[user].append((price, units))

    for row in asks.itertuples(index=False):
        user = row.User
        price = row.Price
        units = row.Unit

        seller_price_dict[user].append((price, units))

    # Sort by price. For buyers, in descending order, sellers, in ascending
    # orders.
    for user in buyer_price_dict.keys():
        buyer_price_dict[user] = sorted(buyer_price_dict[user], reverse=True)

    for user in seller_price_dict.keys():
        seller_price_dict[user] = sorted(seller_price_dict[user])

    # Meet in the middle from the supply and demand curve
    for buyer, seller in matching.items():
        total_units = 0
        avg_price = 0
        i, j = 0, 0

        while (i < len(buyer_price_dict[buyer]) 
               and j < len(seller_price_dict[seller])):
            # When the buying price is less than the selling price, no trade
            # could happen.
            if buyer_price_dict[buyer][i][0] < seller_price_dict[seller][j][0]:
                break

            min_units = min(buyer_price_dict[buyer][i][1],
                            (seller_price_dict[seller][j][1]))

            total_units += min_units
            avg_price += (buyer_price_dict[buyer][i][0] 
                          + seller_price_dict[seller][j][0]) / 2 * min_units 

            buyer_price_dict[buyer][i][1] -= min_units
            seller_price_dict[seller][j][1] -= min_units

            if buyer_price_dict[buyer][i][1] == 0:
                i += 1

            if seller_price_dict[seller][j][1] == 0:
                j += 1
        
        # Update avg_price
        avg_price /= total_units

        new_row = pd.DataFrame({"User" : [buyer], "Units Bought" : [total_units], "Price" : [avg_price]})
        M.alloc_buyer = pd.concat([M.alloc_buyer, new_row], ignore_index=True)

        new_row = pd.DataFrame({"User" : [seller], "Units Bought" : [total_units], "Price" : [avg_price]})
        M.alloc_seller = pd.concat([M.alloc_seller, new_row], ignore_index=True)


def nash_bargaining(M, matching):
    """
    Nash bargaining. Given a pair of matched participants,
    a buyer A and a seller B. Under Nash bargaining mechanism,
    one aims to set a price p such that the following is 
    maximized:
        (u_A(p) - u'_A)) * (u_B(p) - u'(B))
    where u_A(p) and u_A(p) are the payoffs that A and B receive
    under the price p, respectively; u'_A and u'_B are the payoffs
    if no trade happens.

    Source: Nash, J. F. (1950). The bargaining problem. 
    Econometrica, 18(2), 155-162.

    We assume that u'_A and u'_B are zeros. It follows that, an analytical
    optimal solution can be computed, which equals to the middle price.

    Args:
        M (a market instance): 
            The market where bargaining happens

        matching (dict): 
            The buyer-seller matching returned by the matching mechanism.
    
    Returns:
        None
        The two attributes: alloc_seller and alloc_buyer of M are updated to 
        record the resulting allocations.

    """

    # The solution is the same as meeting-in-the-middle.
    middle_bargaining(M, matching)

# --- Factory ---
BARGAIN_METHODS = {
    "nash": nash_bargaining,
    "middle": middle_bargaining
}