""" A pooled market
"""

from marketlib.markets import market
from marketlib.utils import bidask as ba
# from typing import override  # Need Python 3.12

class PoolMarket(market.Market):
    """ A pooled based market. 

    Note: if the total supply quantity does not equal to the total demand quantity, then the problem of maximizing volume is NOT the same as minimizing the gap.
    """

    def _compute_clearing_price(self):
        """
        1. Sort the union of ask and bid prices in non-descending order.
        2. Iterate over each price, compute the corresponding volume.
        3. Return the price with the highest volume.

        Note: the volume should be non-decreasing as price increases to the volume-maximizing price. Therefore,  once we see the volume start to decrease, the previous price is then the target price.

        Returns:
            A tuple consists of three elements: a volume-maximizing price
            (float), the clearing volume (int), and the gap (int)
        """

        # self.book is the orderbook that stores all active bids and asks.
        # Functions get_bids() / get_asks() returns an array of the form: 
        # [bid/ask_price, unit].
        bids = self.book.get_bids().tolist()
        asks = self.book.get_asks().tolist()

        if len(bids) == 0:
            print("There are no active bids.")
            return 0, 0, 0

        elif len(asks) == 0:
            print("There are no active asks.")
            return 0, 0, 0

        # Since prices are already sorted in bids and asks, the operations below can be done in linear time where no additional sorting is needed.
        prices = [x[0] for x in bids] + [y[0] for y in asks]
        prices = sorted(set(prices))

        cumu_bids, cumu_asks = {}, {}  # cumu_bids/asks: [bid/ask_price, number of feasible units].

        for i in range(0, len(bids)):
            if i == 0:
                cumu_bids[bids[i][0]] = bids[i][1]
            else:
                cumu_bids[bids[i][0]] = bids[i][1] + cumu_bids[bids[i-1][0]]
        
        for i in range(0, len(asks)):
            if i == 0:
                cumu_asks[asks[i][0]] = asks[i][1]
            else:
                cumu_asks[asks[i][0]] = asks[i][1] + cumu_asks[asks[i-1][0]]

        # Compute the target price by iterating over all prices sorted in non-descending order.
        curr_vol, curr_gap = -1, -1

        for i in range(len(prices)):
            new_vol, new_gap = ba.compute_vol(prices[i], cumu_bids, cumu_asks)

            if new_vol < curr_vol:  # this never gets called at i = 0.
                return prices[i-1], curr_vol, curr_gap

            curr_vol = new_vol
            curr_gap = new_gap 

        return prices[-1], curr_vol, curr_gap

    # @override
    def clearing(self):
        """ Performs market clearing, which involves two steps:
        
        The clearing mechanism:
            1. Clearing price:
                Find the price that allows largest feasible volume of trades.
            2. Resource allocation:
                Allocation the feasible goods among the buyers, distribute the money among the sellers.
        """

        clearing_price, volume, gap = self._compute_clearing_price()

        # Allocation functions are not class methods.
        # After an allocation, self.alloc_buyers/sellers are updated.
        if clearing_price != 0:
            self.alloc_method(self, clearing_price, volume)  

        print("\n---- Clearning Info ----")

        print(f"Clearing price: {clearing_price}")
        print(f"Total volume: {volume}")
        print(f"Gap: {gap}")

        print("\n---- Buyer Allocation ----")
        print(self.alloc_buyer)

        print("\n---- Seller Allocation ----")
        print(self.alloc_seller)

if __name__ == "__main__": # python3 -m marketlib.markets.pool

    allocation_methods = ["proportional", "uniform", "price", "welfare"]

    for alloc_type in allocation_methods:
        P = PoolMarket(alloc_type=alloc_type, divisible=True)

        P.bid_csv("./data/example_bids.csv")
        P.ask_csv("./data/example_asks.csv")

        P.clearing()

    """ 
    1. Proportional:

    ---- Clearning Info ----
    Clearing price: 2.0
    Total volume: 19
    Gap: 6

    ---- Buyer Allocation ----
        User  Units Bought  Price
    0    3           7.6    2.0
    1    4           3.8    2.0
    2    5           7.6    2.0

    ---- Seller Allocation ----
        User  Units Sold  Price
    0    0        11.0    2.0
    1    1         5.0    2.0
    2    2         3.0    2.0

    2. Uniform:

    ---- Clearning Info ----
    Clearing price: 2.0
    Total volume: 19
    Gap: 6

    ---- Buyer Allocation ----
    User  Units Bought  Price
    0    3      6.333333    2.0
    1    4      6.333333    2.0
    2    5      6.333333    2.0

    ---- Seller Allocation ----
    User  Units Sold  Price
    0    0    6.333333    2.0
    1    1    6.333333    2.0
    2    2    6.333333    2.0
    3    0    6.333333    2.0

    3. Price: 

    ---- Clearning Info ----
    Clearing price: 2.0
    Total volume: 19
    Gap: 6

    ---- Buyer Allocation ----
    User Units Bought  Price
    0    5           10    2.0
    1    3            9    2.0

    ---- Seller Allocation ----
    User Units Sold  Price
    0    2          3    2.0
    1    1          5    2.0
    2    0         11    2.0

    4. Welfare: 

    ---- Clearning Info ----
    Clearing price: 2.0
    Total volume: 19
    Gap: 6

    ---- Buyer Allocation ----
    User Units Bought  Price
    0    3            9    2.0
    1    5           10    2.0

    ---- Seller Allocation ----
    User Units Sold  Price
    0    0         11    2.0
    1    1          5    2.0
    2    2          3    2.0
    """
