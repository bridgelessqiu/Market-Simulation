""" Some general utility functions.
"""

from collections import defaultdict

# ------------------------------
#   Compute preference lists   -
# ------------------------------
def preference_list(bids, asks):
    """ Compute the preference list of buyers and sellers.
    """
    # {participant_id : [average_price_per_unit, total_units]}
    buyer_price_dict, seller_price_dict = {}, {}

    # Construct buyer_price_dict
    for row in bids.itertuples(index=False):
        buyer = row.User
        units = row.Unit
        price = row.Price
        
        if buyer not in buyer_price_dict:
            buyer_price_dict[buyer] = [price, units]
        else:
            buyer_price_dict[buyer][0] = ((buyer_price_dict[buyer][0] * buyer_price_dict[buyer][1]) + price * units) / (units + buyer_price_dict[buyer][1])

            buyer_price_dict[buyer][1] += units

    # Construct seller_price_dict
    for row in asks.itertuples(index=False):
        seller = row.User
        units = row.Unit
        price = row.Price
        
        if seller not in seller_price_dict:
            seller_price_dict[seller] = [price, units]
        else:
            seller_price_dict[seller][0] = ((seller_price_dict[seller][0] * seller_price_dict[seller][1]) + price * units) / (units + seller_price_dict[seller][1])

            seller_price_dict[seller][1] += units

    # Buyer/seller preference list format:
    # {buyer_id : {seller id : utility}}, {seller_id : {buyer id : utility}}    
    # Utility between i and j is the different between their per-unit price 
    # times the number trading units.
    buyer_pref_dict, seller_pref_dict = defaultdict(dict), defaultdict(dict)

    for buyer, p_buyer in buyer_price_dict.items():
        for seller, p_seller in seller_price_dict.items():
            util = (p_buyer[0] - p_seller[1]) * min(p_buyer[1], p_seller[1])
            buyer_pref_dict[buyer][seller] = util
            seller_pref_dict[seller][buyer] = util
    
    return buyer_pref_dict, seller_pref_dict
