"""The base class for different markets.
"""

from marketlib.markets import orderbook as ob
from marketlib.utils import allocation as alloc
from abc import abstractmethod
import pandas as pd

class Market():
    """ The base market class.

    Attributes:
        book (OrderBook): 
            Tracks all active bids and asks.
        divisible (bool, default=True): 
            If goods are divisible, fractional assignments are allowed.
        alloc_buyer (Dataframe):
            Stores results for buyers after market clearing.
        alloc_seller (Dataframe):
            Stores results for sellers after market clearing.
        alloc_method (function, default=UNIFORM):
            The allocation method used by the market. 
    """

    def __init__(self, alloc_type: str="uniform", divisible: bool=True):
        """ A market instance.

        Args:
            alloc_type (str, optional): 
                The name of the allocation method used after computing a clearing price.
            divisible (bool, optional): 
                If goods are divisible, fractional assignments are allowed. 

        Raises:
            ValueError: The allocation method dose not exist.
        """

        # An OrderBook instance has the following four columns: 1. "Unit", 
        # 2. "Price", 3. "Type", and 4. "User".
        self.book = ob._OrderBook()
        self.divisible = divisible
        
        # Placeholders to later store results after clearing.
        # Units bought and sold for a user can be zero
        self.alloc_buyer = pd.DataFrame(columns=["User", "Units Bought", "Price"])
        self.alloc_seller = pd.DataFrame(columns=["User", "Units Sold", "Price"])

        # Currently, four allocation methods are implemented: 1. "uniform", 
        # 2. "price", 3. "welfare", and 4. "proportional".
        if alloc_type not in alloc.ALLOCATION_METHODS:
            raise ValueError(f"Invalid allocation method: {alloc_type}")

        self.alloc_method = alloc.ALLOCATION_METHODS[alloc_type]

    def bid(
        self,
        unit : float,
        price : float,
        user_id : int
    ):
        """ Add one bid to the orderbook.

        Args:
            unit (int): 
                Number of units for this bid 
            price (float): 
                Bid (per-unit) price
            user_id (int): 
                Corresponding user id
        """

        self.book.add_bid(unit, price, user_id)
    
    def bid_csv(self, input_path : str):
        """ Add a collection of bids to the orderbook.

        Args:
            input_path (str): 
                Path to the .csv file. Columns: Unit, Price, User
        """
        self.book.add_bid_csv(input_path)

    def ask(
        self,
        unit : float,
        price : float,
        user_id : int
    ):
        """ Add one ask to the orderbook.

        Args:
            unit (int): 
                Number of units for this ask 
            price (float):
                Ask (per-unit) price
            user_id (int): 
                Corresponding user id
        """ 
        self.book.add_ask(unit, price, user_id)
    
    def ask_csv(self, input_path : str):
        """ Add a collection of asks to the orderbook.

        Args:
            input_path (str): 
                path to the .csv file. Columns: Unit, Price, User
        """
        self.book.add_ask_csv(input_path)
    
    def show(self, scale: int = 0):
        """ Returns the dataframe.

        Args:
            scale (int, Optional): 
                0: both bids and asks.
                1: bids only; 2: asks only.

        Returns:
            A dataframe consists of the orders.
        """
        self.book.display(scale)
    
    @abstractmethod
    def clearing(self):
        """ Market clearing.
        
        Different clearing mechanisms are implemented. Such as pooled, bilateral and auctions.
        """
        raise NotImplementedError("The clearing method should be implemented by each market.")

    def plot(self):
        """ Plot the supply and demand curve
        """
        self.book.plot_curves()


if __name__ == "__main__":  # Call marketlib.markets.market
    M = Market()

    # We assumes that buyers and sellers do not overlap.
    M.bid(10, 2, 0)
    M.bid(5, 1, 1)
    M.ask(10, 5, 2)
    M.ask(6, 0.45, 3)

    print(M.show())
    """
       Ind  Unit Price Type User
        0   10     2  bid    0
        1    5     1  bid    1
        2   10     5  ask    2
        3    6  0.45  ask    3
    """