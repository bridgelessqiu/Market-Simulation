from marketlib.markets import market as mar
from marketlib.utils import bargain as bar
from marketlib.utils import matching as match
import os, random, csv

class BilateralMarket(mar.Market):
    """ A bilateral market.
    
    Participants are paired via a matching mechanism. Then, for each pair, a  bargaining process occurs where price and trade volume are determined. 

    Attributes:
        matching_method (function):
            The matching mechanism used by the market.
        bargain_method (function):
            The bargain procedure used by each pair of participants.
    """

    def __init__(self, 
            production_unit=None,
            decision=None,
            user_num=10,
            matching_type="random", 
            bargain_type="middle",
            ):
        """A bilateral market.

        Args:
            production_unit, decision: For now, these two are dummy variables. 
            matching_type (str, optional): 
                The name of the matching method. Defaults to "random".
            bargain_type (str, optional): 
                The name of the bargaining method. Defaults to "middle".

        Raises:
            ValueError: The matching method or bargaining method dose not exist.
        """

        super().__init__()

        if matching_type not in match.MATCHING_METHODS:
            raise ValueError(f"Invalid matching method: {matching_type}")

        if bargain_type not in bar.BARGAIN_METHODS:
            raise ValueError(f"Invalid bargaining method: {bargain_type}")
        
        self.matching_method = match.MATCHING_METHODS[matching_type]
        self.bargain_method = bar.BARGAIN_METHODS[bargain_type]

        # TODO: Later, we will decide how to use production units and decisions to 
        # assign buyer, sellers, and price.
        # For now, it is random
        os.makedirs("./data", exist_ok=True)

        sellers = [x for x in range(user_num//2)]
        buyers = [x for x in range(user_num//2, user_num)]

        asks = []
        bids = []

        # Two asks per seller
        for s in sellers:
            for _ in range(2):
                unit = random.randint(1, 10)
                price = round(random.uniform(0.5, 3.0), 2)
                asks.append((unit, price, s))

        # Two bids per buyer
        for b in buyers:
            for _ in range(2):
                unit = random.randint(1, 10)
                price = round(random.uniform(1.0, 5.0), 2)
                bids.append((unit, price, b))

        # Write asks.csv
        with open("./data/example_asks.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Unit", "Price", "User"])
            writer.writerows(asks)

        # Write bids.csv
        with open("./data/example_bids.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Unit", "Price", "User"])
            writer.writerows(bids)

    def clearing(self):
        """ Market clearing.

        The clearing is a two-step process:
            1. Matching 
            2. Bargaining
        """

        matching = self.matching_method(self)
        self.bargain_method(self, matching)

if __name__ == "__main__":
    M = BilateralMarket(matching_type="greedy")

    M.bid_csv("./data/example_bids.csv")
    M.ask_csv("./data/example_asks.csv")

    M.clearing()

    print(M.alloc_buyer)
    print(M.alloc_seller)