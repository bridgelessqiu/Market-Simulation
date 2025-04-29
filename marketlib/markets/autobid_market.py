from marketlib.markets import market as mar
from marketlib.utils import auction
from typing import Dict

class AutobidMarket(mar.Market):
    """ Auctions using auto-bidding.

    A market with n players over m divisible items. Each player i has
    a non-negative valuation v_{i,j} for each (full) item j, and a total 
    budget of B_i.

    This market then consist of m first-price auctions, where the bid amount 
    for each player i for item j is alpha_i * v_{i,j}. Here, alpha_i <= 1 is 
    known as the pacing multiplier, computed by the market.

    The goal is to tightly pace the bids for players using the pacing multipliers, 
    such that each player uses its budget as much as possible while not exciting it.

    Attributes:
        data (Dataframe): 
            Stores information about users (i.e., id, valuations, budgets)
        multipliers (Dict):
            Stores the computed pacing multiplier of each user.
        user_item_alloc (Dataframe):
            Stores the cleaning information after the auction.
    """

    def __init__(self, data):
        """ A market that uses auto-bidding. 

        Args:
            data (Dataframe):
            User_id, v_{i,1}, ..., v_{i,m}, Budget
        """
        super().__init__()

        self.data = data
        self.multipliers = {}  # {User : multiplier}

        # We uses the long format to record each allocation of  
        # an item to a user
        columns = ["User", "Item", "Units bought", "Price"]
        self.user_item_alloc = pd.DataFrame(columns=columns)


    def clearing(self):
        """ Market clearing with auto-bidding
        """
        ...
    
if __name__ == "__main__":
   ... 