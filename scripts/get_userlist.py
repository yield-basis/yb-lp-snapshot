# This is only needed because Ethereum node software tends to LOSE EVENTS
# TODO: report bug to Erigon
# This asks another RPC, so we fetch events from several nodes and combine

from brownie import Contract
from brownie import config
from brownie import web3
from brownie import multicall
from datetime import datetime
import json
from collections import defaultdict

from pprint import pprint

config['autofetch_sources'] = True

START = 23434000
END = 23575553  # End of season 1
SIZE = 500
BASE = 10**18


def main():
    total_time = 0
    factory = Contract("0x370a449FeBb9411c95bf897021377fe0B7D100c0")
    lts = [Contract(factory.markets(i)[3]) for i in range(3)]
    gauges = [Contract(factory.markets(i)[-1]) for i in range(3)]
    gauge_addrs = set([g.address for g in gauges])
    print(gauge_addrs)

    users_to_check = [set(), set(), set()]

    for block in range(START, END - (SIZE - 1), SIZE):
        tokens = defaultdict(float)
        print(block)

        for i in range(3):
            for contract in [lts[i], gauges[i]]:
                transfers = contract.events.Transfer.get_logs(fromBlock=block, toBlock=block+SIZE)  # In principle it's + SIZE-1, but let's be safu
                users_to_check[i].update(str(ev.args.sender) for ev in transfers if ev.args.sender not in gauge_addrs)
                users_to_check[i].update(str(ev.args.receiver) for ev in transfers if ev.args.receiver not in gauge_addrs)

    with open("all_users.json", "w") as f:
        json.dump([list(u) for u in users_to_check], f)
