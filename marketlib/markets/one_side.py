from marketlib.markets import market as mar
from marketlib.utils import auction
from typing import Dict

class OneSideMarket(mar.Market):
    """ One-sided market where only bids or asks are quoted.

    This market supports various auction mechanisms.

    Attributes:
        auction_method (function):
            The auction mechanism used in market clearing.
        bids (dict):
            Contains the bids for each participants of the form:
            {user_id : price}
    """

    def __init__(self, bids : Dict, auction_type : str="first_price"):
        """ A one-sided market.

        Args:
            bids (dict):
                Contains the bids for each participants of the form:
                {user_id : price}
            auction_type (str, optional):
                The name of the auction mechanism used by the market.
        Raise:
            ValueError: The auction method dose not exist.
        """

        super().__init__()

        if auction_type not in auction.AUCTION_METHODS:
            raise ValueError(f"Invalid auction mechanism: {matching_type}")
        
        self.auction_method = auction.AUCTION_METHODS[auction_type]
        self.bids = bids

    def clearing(self):
        """ Market clearing using an auction mechanism.
        """
        self.auction_method(self, self.bids)
    
if __name__ == "__main__":
    bids = {
        1 : 5, 
        2 : 5, 
        3 : 5,
        4 : 1.5,
        5 : 2.4
    }

    M = OneSideMarket(bids=bids, auction_type="reverse") 
    M.clearing()

    print(M.alloc_buyer)