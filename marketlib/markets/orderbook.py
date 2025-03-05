"""Orderbook tracks all active bids and asks

For internal usage only (by the Market class).
"""

import pandas as pd
import matplotlib.pyplot as plt  # type: ignore
from marketlib.utils import bidask as ba

class _OrderBook():
    """ Track of all active bids and asks.

    Attributes:
        orders (dataframe):
            Columns are "Unit", "Price", "Type" and "User". "Price" is
            per-unit, "Type" is bid or ask, "User" is user id.
    """

    col_names = [
        'Unit',
        'Price',
        'Type',
        'User'
    ] 

    def __init__(self):
        self.orders = pd.DataFrame(columns=self.col_names)

    def add_bid(
        self,
        unit,
        price,
        user_id
    ):
        """ Add one bid to the orderbook.

        Args:
            unit (int): 
                Units for this bid 
            price (float): 
                Per-unit bid price
            user_id (int): 
                Buyers and sellers don't overlap
        """

        new_bid = pd.DataFrame([[unit, price, 'bid', user_id]], columns=self.col_names)
        self.orders = pd.concat([self.orders, new_bid], ignore_index=True)

    def add_bid_csv(
        self,
        input_path
    ):
        """ Add a collection of bids to the orderbook.

        Args:
            input_path (str):
                Path to the .csv file. Columns: Unit, Price, User
        """

        new_bid = pd.read_csv(input_path, header=None, names=["Unit", "Price", "User"], sep=',')
        new_bid["Type"] = "bid"
        new_bid = new_bid[["Unit", "Price", "Type", "User"]]

        self.orders = pd.concat([self.orders, new_bid], ignore_index=True)

    def add_ask(
        self,
        unit,
        price,
        user_id
    ):
        """ Add one ask to the orderbook.

        Args:
            unit (int): 
                Units for this ask 
            price (float): 
                Ask price
            user_id (int):
                Buyers and sellers don't overlap
        """  
        
        new_ask = pd.DataFrame([[unit, price, 'ask', user_id]], columns=self.col_names)
        self.orders = pd.concat([self.orders, new_ask], ignore_index=True)

    def add_ask_csv(
        self,
        input_path
    ):
        """ Add a collection of asks to the orderbook.

        Args:
            input_path (str): 
                Path to the .csv file. Columns: Unit, Price, User
        """

        new_ask = pd.read_csv(input_path, header=None, names=["Unit", "Price", "User"], sep=',')
        new_ask["Type"] = "ask"
        new_ask = new_ask[["Unit", "Price", "Type", "User"]]

        self.orders = pd.concat([self.orders, new_ask], ignore_index=True)

    def display(self, scale=0):
        """ Return the orderbook.

        Args:
            scale (int, default=0): 
                0: both bids and asks; 
                1: bids; 2: asks

        Returns:
            Dataframe, the orderbook
        """

        if scale == 0:
            return self.orders
        elif scale == 1:
            return [self.orders['Type'] == 'bid']
        else:
            return self.orders[self.orders['Type'] == 'ask']

    def get_bids(self):
        """ Extract all bids, sorted in non-ascending order by prices. Bids of the same prices are merged.

        Returns:
            A numpy array of the form [[bid_price, units] ...]
        """

        bids = self.orders[self.orders['Type'] == 'bid']
        bid_curves = bids.groupby('Price')['Unit'].sum().reset_index()

        return bid_curves.sort_values(by=['Price'], ascending=False).to_numpy()
    
    def get_asks(self):
        """ Extract all asks, sorted in non-descending order by prices. Asks of the same prices are merged.

        Returns:
            A numpy array of the form [[ask_price, units] ...]
        """

        asks = self.orders[self.orders['Type'] == 'ask']
        ask_curves = asks.groupby('Price')['Unit'].sum().reset_index()

        return ask_curves.sort_values(by=['Price']).to_numpy()

    def plot_curves(self):
        """ Plot the supply & demand curve as two step functions.
        """

        demand_curve = self.get_bids().tolist()
        supply_curve = self.get_asks().tolist()

        demand_units = [unit for price, unit in demand_curve]
        demand_prices = [price for price, unit in demand_curve]
        cumulative_demand = [0] + list(ba.cumu_sum(demand_units))
    
        supply_units = [unit for price, unit in supply_curve]
        supply_prices = [price for price, unit in supply_curve]
        cumulative_supply = [0] + list(ba.cumu_sum(supply_units))
    
        demand_prices = demand_prices + [demand_prices[-1]]
        supply_prices = supply_prices + [supply_prices[-1]]

        plt.figure(figsize=(7, 4), dpi=450)
        
        plt.step(cumulative_demand, demand_prices, label='Demand', where='post', 
                 color='#1f77b4', linewidth=2.5, alpha=0.8)
        plt.step(cumulative_supply, supply_prices, label='Supply', where='post', 
                 color='#ff7f0e', linewidth=2.5, alpha=0.8)
    
        plt.title('Demand & Supply Curves', fontsize=14, fontweight='bold')
        plt.xlabel('Quantity', fontsize=12)
        plt.ylabel('Price', fontsize=12)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), frameon=True, fontsize=10, ncol=2)
        plt.grid(True, linestyle='--', alpha=0.6)
    
        # Show the plot
        plt.tight_layout()  
        plt.show()
    

if __name__ == "__main__":
    B = _OrderBook() # Run: python3 -m marketlib.markets.orderbook

    B.add_bid(5, 1, 0)
    B.add_bid(10, 1.5, 1)
    B.add_bid(20, 0.5, 2)
    B.add_ask(7, 0.85, 3)
    B.add_ask(12, 1.15, 4)

    print(B.display())

    """ 
    Ind  Unit Price Type User
    0    5     1  bid    0
    1   10   1.5  bid    1
    2   20   0.5  bid    2
    3    7  0.85  ask    3
    4   12  1.15  ask    4
    """