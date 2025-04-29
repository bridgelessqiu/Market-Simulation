from marketlib.utils import valuation
from marketlib.markets import bilateral
import os
import csv

class Agent():
    """The class for a single agent.
    """

    def __init__(self, 
                rank : int, 
                N : int, 
                k : int, 
                delta : float, 
                beta : float,
                ):
        """ Create an agent.

        Args:
            rank (int):
                The priority rank of the agent. Needed to determine if it
                is a seller.
            N (int): 
                The number of agents. This is needed to determine if an 
                agent is a buyer or a seller.
            k (int): 
                The units of water.
            delta (float): 
                The fraction of the water that is available.
            beta (float):
                The parameter to compute the valuation.
        """

        self.rank = rank
        self.N = N
        self.k = k 
        self.delta = delta 

        self.type = "buyer"
        if valuation.is_seller(rank, N, delta):  # If rank/n >= 1 - \delta
            self.type = "seller"
        
        k1 = k // 3
        k2 = k - k1
        self.value = valuation.compute_valuation(beta, k1, k2, self.type)

    def __repr__(self):
        return (f"Agent {self.rank} | {self.k} units of water | {self.type} | price: {self.value}")

class Agents():
    """
    The class for a collection of agents.
    """

    def __init__(self, 
                N : int=10, 
                delta : float=0.5, 
                k : int = 5, 
                beta_l : float = 0.3, 
                beta_h : float = 0.7,
                lamb : float = 0.6
                ):

        """A collection of agents.
        
        Args:
            N (int): 
                The number of agents.
            delta (float):
                The fraction of the water that is available.
            k (int):
                The number of units of water.
            beta_l (float):
                The beta for low-valuation users.
            beta_h (float):
                The beta for high-valuation users.
        """
    
        self.agents = []

        for rank in range(1, N + 1):
            beta = beta_l
            if valuation.is_high_value(lamb, rank, N):
                beta = beta_h

            agent = self._create_agents(rank, N, k, delta, beta)
            self.agents.append(agent)
        
        self._export_orderbook()

    def _create_agents(self, rank, N, k, delta, beta):
        agent = Agent(rank, N, k, delta, beta)
        return agent
    
    def _export_orderbook(self):
        bids, asks = [], []

        for agent in self.agents:
            for _, (units, price_per_unit) in agent.value.items():
                row = [units, price_per_unit, agent.rank]
                if agent.type == "buyer":
                    bids.append(row)
                else:
                    asks.append(row)

        directory = "./data" 
        os.makedirs(directory, exist_ok=True)

        with open(os.path.join(directory, "bids.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Unit", "Price", "User"])
            writer.writerows(bids)
        
        with open(os.path.join(directory, "asks.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Unit", "Price", "User"])
            writer.writerows(asks)
    
    def update_prices(self, alloc_buyer, alloc_seller, epsilon=0.1):
        ...

if __name__ == "__main__":  # Will most to test eventually
    agent_config = {
    "N": 10,
    "delta": 0.5,
    "k": 6,
    "beta_l": 0.3,
    "beta_h": 0.7,
    "lamb": 0.65
    }

    A = Agents(**agent_config)
    M = bilateral.BilateralMarket(matching_type="greedy")

    M.bid_csv("./data/bids.csv")
    M.ask_csv("./data/asks.csv")

    M.clearing()
    M.show()

    print(M.alloc_buyer)
    print(M.alloc_seller)