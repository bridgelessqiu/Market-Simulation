"""
The utilities are for developers only.
  1. They are not accessible to users. 
  2. Should not be imported automatically.
  3. Should not appear in the doc.
"""

from typing import Dict
import networkx as nx # type: ignore
import random
from marketlib.utils import general

# ------------------ #
#  Stable Matching   #
# ------------------ #
def stable_matching(M) -> Dict:
    """ Stable matching algorithm.

    Given a set of buyers and a set of sellers, we first
    compute a preference list of each participant. Then 
    we do stable matching (Gale-Shapley).

    Args:
        M (Market): 
            A market instance.          
            Note: We assume that the number of buyers equals to
            the number of sellers.

    Returns:
        A dict that contains one-to-one matching between the 
        buyers and the sellers. 
    """

    bids = M.book.orders[(M.book.orders["Type"] == "bid")]
    asks = M.book.orders[(M.book.orders["Type"] == "ask")]

    # Buyer/seller preference list format:
    # {buyer_id : {seller id : utility}}, {seller_id : {buyer id : utility}}    
    # Utility between i and j is the different between their per-unit price 
    # times the number trading units.
    buyer_pref_dict, seller_pref_dict = general.preference_list(bids, asks)

    # Sort by utility 
    for buyer in buyer_pref_dict.keys():
        buyer_pref_dict[buyer] = list(sorted(buyer_pref_dict[buyer].keys(), key=lambda x: buyer_pref_dict[buyer][x], reverse=True))
    
    for seller in seller_pref_dict.keys():
        seller_pref_dict[seller] = list(sorted(seller_pref_dict[seller].keys(), key=lambda x: seller_pref_dict[seller][x], reverse=True))

    # Stable Matching
    free_buyers = list(buyer_pref_dict.keys())
    buyer_match = {buyer: None for buyer in buyer_pref_dict}
    seller_match = {seller: None for seller in seller_pref_dict}

    seller_rank = {
        seller: {buyer: rank for rank, buyer in enumerate(preferences)}
        for seller, preferences in seller_pref_dict.items()
    }

    # Gale-Shapley algorithm
    while free_buyers:
        buyer = free_buyers.pop(0)  # Get a free buyer
        buyer_preferences = buyer_pref_dict[buyer]

        for seller in buyer_preferences:
            current_partner = seller_match[seller]

            # If seller is free, match buyer and seller
            if current_partner is None:
                buyer_match[buyer] = seller
                seller_match[seller] = buyer
                break

            # If seller prefers the new buyer over the current partner
            elif seller_rank[seller][buyer] < seller_rank[seller][current_partner]:
                # Break the current match
                buyer_match[current_partner] = None
                free_buyers.append(current_partner)

                # Match the new buyer and seller
                buyer_match[buyer] = seller
                seller_match[seller] = buyer
                break
    
    return buyer_match
    
# ----------------- #
#  Random Matching  #
# ----------------- #
def random_matching(M):
    """ A random matching between the buyers and sellers.

    Args:
        M (Market): 
            A market instance.          
            Note: We assume that the number of buyers equals to
            the number of sellers.

    Returns:
        A dict that contains one-to-one matching between the 
        buyers and the sellers. 
    """

    buyers = M.book.orders.loc[M.book.orders["Type"] == "bid", "User"].unique().tolist()

    sellers = M.book.orders.loc[M.book.orders["Type"] == "ask", "User"].unique().tolist()
    random.shuffle(sellers)

    return dict(zip(buyers, sellers))

# ----------------------- #
#  Max Weighted Matching  #                
# ----------------------- #
def maximum_weighted_matching(M):
    """ Solve a maximum weighted bipartite matching problem.

    The Weight of each pair (i, j) is the utility value computed as 
    follows:
        (i's per_unit price - j's per_unit price) * min(i's volume, j' volume)

    Args:
        M (Market): 
            A market instance.          
            Note: We assume that the number of buyers equals to
            the number of sellers.

    Returns:
        A dict that contains one-to-one matching between the 
        buyers and the sellers.
    """
    bids = M.book.orders[(M.book.orders["Type"] == "bid")]
    asks = M.book.orders[(M.book.orders["Type"] == "ask")]

    # Buyer/seller preference list format:
    # {buyer_id : {seller id : utility}}, {seller_id : {buyer id : utility}}    
    # Utility between i and j is the different between their per-unit price 
    # times the number trading units.
    buyer_pref_dict, _ = general.preference_list(bids, asks)

    # Maximum weighted bipartite matching
    G = nx.Graph(nodetype=int)
    for u in buyer_pref_dict.keys():
        for v, w in buyer_pref_dict[u].items():
            G.add_edge(u, v, weight=w)

    final_matching = nx.bipartite.maximum_matching(G)

    # The format of final_matching is {user : matched_user}, where the left 
    # hand side of a pair can be either a buyer or a sellers. This creates
    # duplicates. Therefore, we only extract the matching where buyers are on
    # the left-hand side.
    return {u : v for u, v in final_matching.items() if u in buyer_pref_dict.keys()}

# ------------------ #
#   Greedy Matching  #
# ------------------ #
def greedy_matching(M):
    """ Solve a greedy matching problem.

    The Weight of each pair (i, j) is the utility value computed as 
    follows:
        (i's per_unit price - j's per_unit price) * min(i's volume, j' volume)
    The market then greedily selects the next (previously unmatched) pair to be
    matched.

    Args:
        M (Market): 
            A market instance.          
            Note: We assume that the number of buyers equals to
            the number of sellers.

    Returns:
        A dict that contains one-to-one matching between the 
        buyers and the sellers.
    """
    bids = M.book.orders[(M.book.orders["Type"] == "bid")]
    asks = M.book.orders[(M.book.orders["Type"] == "ask")]

    # Buyer/seller preference list format:
    # {buyer_id : {seller id : utility}}, {seller_id : {buyer id : utility}}    
    # Utility between i and j is the different between their per-unit price 
    # times the number trading units.
    buyer_pref_dict, _ = general.preference_list(bids, asks) 

    sorted_pairs = sorted(
        [(util, (u, v)) for u, x in buyer_pref_dict.items() for v, util in x.items()], reverse=True
    )

    # Greedy matching
    seen_seller = set()
    final_matching = {}
    for _, p in sorted_pairs:
        u, v = p

        if v in seen_seller:
            continue
        if u in final_matching.keys():
            continue

        final_matching[u] = v
        seen_seller.add(v)
    
    return final_matching

# --- Factory ---
MATCHING_METHODS = {
    "random": random_matching,
    "stable": stable_matching,
    "maximum": maximum_weighted_matching,
    "greedy": greedy_matching
}