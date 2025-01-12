from .orderbook import OrderBook
from abc import ABC, abstractmethod

class Market():
    """
    The base market class. It supposts the following methods:

    bid (function): add a bid
    ask (function): add an ask
    clearing (function): perform market clearing. Abstract method.
    plot (function): plot the supply/demand curve
    """

    def __init__(self):
        self.book = OrderBook()

    def bid(
        self,
        unit,
        price,
        user_id
    ):
        """
        Add one bid to the orderbook.

        Args:
            unit (int): units for this bid 

            price (float): bid price

            user_id (int): corresponding user id
        """
        self.book.add_bid(unit, price, user_id)
    
    def bid_csv(self, input_path):
        """
        Add a collection of bids to the orderbook.

        Args:
            input_path (str): path to the .csv file.
            Unit, Price, User
        """
        self.book.add_bid_csv(input_path)

    def ask(
        self,
        unit,
        price,
        user_id
    ):
        """
        Add one ask to the orderbook.

        Args:
            unit (int): units for this ask 

            price (float): ask price

            user_id (int): corresponding user id
        """ 
        self.book.add_ask(unit, price, user_id)
    
    def ask_csv(self, input_path):
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
    def clearing(self, bids, asks):
        """
        Clearning function. This depends on the base class.
        """
        pass

    def plot(self):
        """
        Plot the supply and demand curve
        """
        self.book.plot_curves()