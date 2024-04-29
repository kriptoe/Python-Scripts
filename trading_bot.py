# A simple buy and sell bot. Set the buy and sell prices
# When the buy is filled, the script then places the sell order and vice versa
# Hopefully the asset goes up and down through the set range

import json
from open_orders_util import get_open_orders
from getBalances import get_spot_asset_balances
from hyperliquid.utils import constants
import example_utils
import time

COIN = "PURR/USDC"
CUURENT_ORDER = "BUY"
# places a spot order 
#parameters - name of coin, amount of coins to be purchased, price you want to buy at
def buySpotOrder(coinName, amount, price):
    address, info, exchange = example_utils.setup(base_url=constants.MAINNET_API_URL, skip_ws=True)
    # Place a BUY order for 5 PURR at $90 per coin
    order_result = exchange.order(coinName, True, amount, price, {"limit": {"tif": "Gtc"}})
    return order_result
 
def cancelSpotOrder(order_data):
        # Cancel the order
    if order_data["status"] == "ok":
        status = order_data["response"]["data"]["statuses"][0]
        if "resting" in status:
            cancel_result = order_data.cancel(COIN, status["resting"]["oid"])
            print(cancel_result)


# Function to place a spot sell order
def sellSpotOrder(coinName, amount, price):
    address, info, exchange = example_utils.setup(base_url=constants.MAINNET_API_URL, skip_ws=True)
    # Place a SELL order for the specified coin
    print("price-------------------- ", price)
    order_result = exchange.order(coinName, False, amount, price, {"limit": {"tif": "Gtc"}})
    return order_result

# Function to check if an order has been filled
def checkOrderFilled(order_id):
    address, info, exchange = example_utils.setup(base_url=constants.MAINNET_API_URL, skip_ws=True)
    order_info = exchange.order_info(COIN, order_id)
    if order_info["status"] == "ok":
        if order_info["response"]["data"]["state"] == "filled":
            return True
    return False

def main():
    address, info, exchange = example_utils.setup(base_url=constants.MAINNET_API_URL, skip_ws=True)

    # Get the user state and print out position information
    spot_user_state = info.spot_user_state(address)
    if len(spot_user_state["balances"]) > 0:
        print("spot balances:")
        for balance in spot_user_state["balances"]:
            print(json.dumps(balance, indent=2))
    else:
        print("no available token balances")

    SELL_PRICE = 0.1047
    BUY_PRICE = 0.0967
    AMOUNT= 625   # amount of coins to buy

    #CURRENT_ORDER="SELL"  # tells program to buy

    # ---------------- SELL ------------------- #
    CURRENT_ORDER="SELL"  # tells program to sell

    if CURRENT_ORDER=="BUY":
    # SELL ORDER
        sell_order_result = sellSpotOrder(COIN, AMOUNT, SELL_PRICE)
        order_result= sell_order_result
        CURRENT_ORDER="SELL"   
    else:
    #BUY ORDER
        buy_order_result = buySpotOrder(COIN, AMOUNT, BUY_PRICE)
        order_result=buy_order_result
        CURRENT_ORDER="BUY"

    print(order_result)

    time.sleep(5)

    # Check if the sell order was successful
    user_address = "0x2a21Cc5D8Bcaa0D10078C99606B03Ee46C58817d"
    while True:
        open_orders, has_open_orders = get_open_orders(user_address)
        if has_open_orders:
            print("Open Orders:")
            for order in open_orders:
                print(order)
        else:
            print("There are no open orders for this user.")
            if CURRENT_ORDER=="BUY":
                # SELL ORDER
                purr_balance = get_spot_asset_balances(user_address, "PURR")  # get the wallet's balance of PURR
                if purr_balance > AMOUNT:    # if the amount of PURR has increased from a trade, update the AMOUNT
                    AMOUNT=purr_balance
                    print("New amount of PURR is ", purr_balance)
                sell_order_result = sellSpotOrder(COIN, AMOUNT, SELL_PRICE)
                order_result= sell_order_result
                CURRENT_ORDER="SELL"   
            else:
            #BUY ORDER
                buy_order_result = buySpotOrder(COIN, AMOUNT, BUY_PRICE)
                order_result=buy_order_result
                CURRENT_ORDER="BUY"
           # Wait 5 mins before checking again
        
        time.sleep(300)


if __name__ == "__main__":
    main()
