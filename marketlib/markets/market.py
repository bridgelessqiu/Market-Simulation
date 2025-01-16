from .orderbook import OrderBook
from abc import ABC, abstractmethod
from utils import allocation as alloc
import pandas as pd

class Market():
    """
    The base market class. It supposts the following methods:

    bid (function): add a bid
    ask (function): add an ask
    clearing (function): perform market clearing. Abstract method.
    plot (function): plot the supply/demand curve
    """

    def __init__(self, alloc_type="proportional", divisble=True):
        self.book = OrderBook()
        self.divisible = divisble
        self.alloc_type = alloc_type
        self.alloc_buyer = pd.DataFrame(columns=["User", "Units Bought", "Price"])
        self.alloc_seller = pd.DataFrame(columns=["User", "Units Sold", "Price"])

        if self.alloc_type not in alloc.ALLOCATION_METHODS:
            raise ValueError(f"Invalid allocation method: {self.alloc_type}")

        self.alloc_method = alloc.ALLOCATION_METHODS[self.alloc_type]

    def bid(
        self,
        unit : float,
        price : float,
        user_id : int
    ):
        """
        Add one bid to the orderbook.

        Args:
            unit (int): units for this bid 

            price (float): bid price

            user_id (int): corresponding user id
        """
        self.book.add_bid(unit, price, user_id)
    
    def bid_csv(self, input_path : str):
        """
        Add a collection of bids to the orderbook.

        Args:
            input_path (str): path to the .csv file.
            Unit, Price, User
        """
        self.book.add_bid_csv(input_path)

    def ask(
        self,
        unit : float,
        price : float,
        user_id : int
    ):
        """
        Add one ask to the orderbook.

        Args:
            unit (int): units for this ask 

            price (float): ask price

            user_id (int): corresponding user id
        """ 
        self.book.add_ask(unit, price, user_id)
    
    def ask_csv(self, input_path : str):
        """
        Add a collection of asks to the orderbook.

        Args:
            input_path (str): path to the .csv file.
            Unit, Price, User
        """
        self.book.add_ask_csv(input_path)
    
    def show(self, scale=0):
        """
        Args:
            scale (int, default=0): 
                0: both bids and asks; 
                1: bids; 2: asks

        Returns:
            dataframe: the orderbook
        """
        return self.book.display(scale)
    
    @abstractmethod
    def clearing(self):
        """
        Clearning function. This depends on the base class.
        """
        pass

    def plot(self):
        """
        Plot the supply and demand curve
        """
        self.book.plot_curves()