import random
import time

# ----------------- 
#   First Price   -
# ----------------- 
def first_price_sealed_bid(bids):
    """ Implements a First-Price Sealed-Bid Auction.
    """
    if not bids:
        return None, 0.0  # No bids, no winner

    # Sort bids in descending order by bid amount
    sorted_bids = sorted(bids, key=lambda x: x[0], reverse=True)

    # The highest bidder wins and pays their bid
    winner_id, winning_bid = sorted_bids[0]

    return winner_id, winning_bid

# ------------------ 
#   Second Price   -
# ------------------ 
def second_price_sealed_bid(bids):
    """
    Implements a Second-Price Sealed-Bid Auction (Vickrey Auction).

    Args:
        bids (list of tuples): List of (bid_amount, bidder_id), where:
            - bid_amount (float): The price offered by the bidder.
            - bidder_id (int): The unique identifier of the bidder.

    Returns:
        tuple: (winner_id, amount_paid)
            - winner_id (int): The ID of the highest bidder.
            - amount_paid (float): The second-highest bid (or 0 if only one bid exists).
    """
    if not bids:
        return None, 0.0  # No bids, no winner

    if len(bids) == 1:
        # Only one bid exists; the winner pays 0 (edge case)
        return bids[0][1], 0.0

    # Sort bids in descending order by bid amount
    sorted_bids = sorted(bids, key=lambda x: x[0], reverse=True)

    # The highest bidder wins but pays the second-highest bid
    winner_id, winning_bid = sorted_bids[0]
    second_price = sorted_bids[1][0]  # The second-highest bid amount

    return winner_id, second_price

# ---------------------
#   English Auction   -
# ---------------------

def english_auction(valuations, min_increment=1.0):
    """
    Implements an English (Ascending) Auction.

    Since this auction is a dynamic process, we model it iteratively: 
    1. Each bidder starts by bidding half of their true valuation. 
    2. Bidding continues in rounds where bidders increase their bids until no one is willing to bid higher than the current highest bid. 
    3. The last remaining bidder wins and pays the final price.

    Args:
        valuations (list of tuples): List of (true_value, bidder_id), where:
            - true_value (float): The maximum price the bidder is willing to pay.
            - bidder_id (int): The unique identifier of the bidder.
        min_increment (float, optional): The minimum bid increment (default is 1.0).

    Returns:
        tuple: (winner_id, amount_paid)
            - winner_id (int): The ID of the winning bidder.
            - amount_paid (float): The final price paid by the winner.
    """
    if not valuations:
        return None, 0.0  # No bidders, no winner

    # Initialize starting bids (half of each bidder's true valuation)
    active_bidders = {bidder_id: value / 2 for value, bidder_id in valuations}

    current_price = max(active_bidders.values())  # Start with the highest initial bid
    highest_bidder = max(active_bidders, key=active_bidders.get)

    while True:
        # Find bidders who can still bid
        bidders_willing_to_bid = [
            (bidder_id, value)
            for value, bidder_id in valuations
            if value > current_price + min_increment  # They can increase their bid
        ]

        if not bidders_willing_to_bid:
            break  # No one wants to bid higher, auction ends

        # Select a random bidder to increase the bid (mimicking real auction dynamics)
        random.shuffle(bidders_willing_to_bid)
        next_bidder, max_value = bidders_willing_to_bid[0]  # Choose one willing bidder

        # Update bid and continue the auction
        current_price += min_increment
        highest_bidder = next_bidder

    return highest_bidder, current_price


# -------------------
#   Dutch Auction   -
# -------------------
def dutch_auction(valuations, start_price=None, price_decrement=1.0, delay=0.1):
    """
    """
    if not valuations:
        return None, 0.0  # No bidders, no winner

    # Determine starting price (default: highest valuation + 10% buffer)
    max_valuation = max(value for value, _ in valuations)
    if start_price is None:
        start_price = max_valuation * 1.1  # Start above the highest valuation

    current_price = start_price

    while current_price > 0:
        # Check if any bidder accepts the current price
        for value, bidder_id in valuations:
            if value >= current_price:
                return bidder_id, current_price  # First bidder to accept wins

        # Lower the price and simulate real-time auction delay
        current_price -= price_decrement
        time.sleep(delay)  # Optional delay for real-world auction simulation

    return None, 0.0  # No bidder accepted before price hit 0

# ---------------------
#   All-pay auction   -
# ---------------------
def all_pay_auction(bids):
    """
    Implements an All-Pay Auction. In an All-Pay Auction, all bidders 
    pay their bid amount regardless of winning. However, the highest 
    bidder wins the auction.

    Args:
        bids (list of tuples): List of (bid_amount, bidder_id), where:
            - bid_amount (float): The price offered by the bidder.
            - bidder_id (int): The unique identifier of the bidder.

    Returns:
        tuple: (winner_id, payments)
            - winner_id (int): The ID of the highest bidder (winner).
            - payments (dict): A dictionary {bidder_id: amount_paid} showing how much each bidder paid.
    """
    if not bids:
        return None, {}  # No bids, no winner

    # Determine the highest bidder
    sorted_bids = sorted(bids, key=lambda x: x[0], reverse=True)
    winner_id, _ = sorted_bids[0]

    # All bidders pay their bid amount
    payments = {bidder_id: bid_amount for bid_amount, bidder_id in bids}

    return winner_id, payments

# ---------------------
#   Double auction   -
# ---------------------
def double_auction(bids):
    """
    This is not needed. Our pooled market is a double auction.
    """
    print("Please use a pooled market instead.")
    pass

# ---------------------
#   Reverse Auction   -
# ---------------------
def reverse_auction(seller_bids):
    """
    Implements a Reverse Auction.

    1. Multiple sellers compete to offer the lowest price.
    2. A single buyer selects the seller with the lowest bid.

    Args:
        seller_bids (list of tuples): List of (offer_price, seller_id), where:
            - offer_price (float): The price the seller is willing to accept.
            - seller_id (int): The unique identifier of the seller.

    Returns:
        tuple: (winner_id, amount_paid)
            - winner_id (int): The ID of the lowest-bidding seller.
            - amount_paid (float): The final price paid by the buyer.
    """
    if not seller_bids:
        return None, 0.0  # No offers, no winner

    # Sort seller offers in ascending order (cheapest offer wins)
    sorted_bids = sorted(seller_bids, key=lambda x: x[0])

    # The lowest-bidding seller wins
    winner_id, winning_bid = sorted_bids[0]

    return winner_id, winning_bid



AUCTION_METHODS = {
    "first_price" : first_price_sealed_bid,
    "second_price": second_price_sealed_bid,
    "english": english_auction,
    "dutch": dutch_auction,
    "all_pay": all_pay_auction,
    "double": double_auction,
    "reverse": reverse_auction
}
