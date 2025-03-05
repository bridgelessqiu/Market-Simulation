from marketlib.markets import market as mar
from marketlib.utils import bargain as bar
from marketlib.utils import matching as match

class BilateralMarket(mar.Market):
    """ A bilateral market.
    
    Participants are paired via a matching mechanism. Then, for each pair, a  bargaining process occurs where price and trade volume are determined. 

    Attributes:
        matching_method (function):
            The matching mechanism used by the market.
        bargain_method (function):
            The bargain procedure used by each pair of participants.
    """

    def __init__(self, matching_type="random", bargain_type="middle"):
        """_summary_

        Args:
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

    def clearing(self):
        """ Market clearning.

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
