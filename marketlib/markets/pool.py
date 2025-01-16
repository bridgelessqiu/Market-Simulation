from .market import Market
from utils import bidask as ba

class PoolMarket(Market):
    """
    A pool-based market. 
    
    The clearing mechanism:
    1. Find the price that allows **largest feasible volume of trades**

    2. If the true clearing price does not exists, also return the gap, 
    which is the excessive amount of either supply or demand.

    Remark: If the total supply quantity does not equal to the total demand quantity, 
    then the problem of maximizing volume is **NOT** the same as minimizing the gap.
    """

    def _pricing(self):
        """
        How the clearing price is found:
        1. Sort the union of ask and bid prices in non-descending order.

        2. Iterative over each price, compute the corresponding volume.

        3. Return the price with the highest volume.
            Note: the resulting volume should be non-decreasing as 
            price increases to the volume-maximizing price. Therefore, 
            once we see the volume start to decrease, the previous price 
            is then the target price to return.

        Returns:
            A volume-maximizing price (float), the volumn, the gap
        """

        bids = self.book.get_bids().tolist()
        asks = self.book.get_asks().tolist()

        # --- Sort the prices ---
        # This can be done in linear time where no sorting is needed
        prices = [x[0] for x in bids] + [y[0] for y in asks]
        prices = sorted(set(prices))

        # --- Compute the cumulative quantity of bids and asks ---
        cumu_bids, cumu_asks = {}, {}

        # --- Compute the cumulative bid/ask units
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

        # --- Compute the target price ---
        curr_vol = -1
        curr_gap = -1

        for i in range(len(prices)):
            new_vol, new_gap = ba.compute_vol(prices[i], cumu_bids, cumu_asks)

            if new_vol < curr_vol: # this never gets called at i = 0
                return prices[i-1], curr_vol, curr_gap

            curr_vol = new_vol
            curr_gap = new_gap 

        return prices[-1], curr_vol, curr_gap

    def clearing(self):
        """
        Peformes market clearing, which involves two stesp:
            1. Compute the clearing price and volume
            2. Determine the allocations
        """
        # --- Compute the clearing price ---
        clearing_price, volume, gap = self._pricing()

        # --- Compute the allocation ---
        # Note: This is not a class method
        self.alloc_method(self, clearing_price, volume)
        
        # --- Output (Optional) --- 
        print("\n---- Clearning Info ----")

        print(f"Clearing price: {clearing_price}")
        print(f"Total volumn: {volume}")
        print(f"Gap: {gap}")

        print("\n---- Buyer Allocation ----")
        print(self.alloc_buyer)

        print("\n---- Seller Allocation ----")
        print(self.alloc_seller)