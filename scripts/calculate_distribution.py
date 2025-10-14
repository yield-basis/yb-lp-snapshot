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
    fraction_days = defaultdict(float)
    mc = Contract("0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696")
    factory = Contract("0x370a449FeBb9411c95bf897021377fe0B7D100c0")
    lts = [Contract(factory.markets(i)[3]) for i in range(3)]
    gauges = [Contract(factory.markets(i)[-1]) for i in range(3)]
    gauge_addrs = set([g.address for g in gauges])
    print(gauge_addrs)

    t0 = web3.eth.get_block(START - 1).timestamp
    users_to_check = [set(), set(), set()]
    lt_balances = defaultdict(dict)
    gauge_balances = defaultdict(dict)

    for block in range(START, END - (SIZE - 1), SIZE):
        tokens = defaultdict(float)

        for i in range(3):
            for contract in [lts[i], gauges[i]]:
                transfers = contract.events.Transfer.get_logs(fromBlock=block, toBlock=block+SIZE-1)
                users_to_check[i].update(ev.args.sender for ev in transfers if ev.args.sender not in gauge_addrs)
                users_to_check[i].update(ev.args.receiver for ev in transfers if ev.args.receiver not in gauge_addrs)

        with multicall(address=mc.address, block_identifier=block+SIZE-1):
            for i in range(3):
                for u in users_to_check[i]:
                    lt_balances[i][u] = lts[i].balanceOf(u)
                    gauge_balances[i][u] = gauges[i].balanceOf(u)
            redemption_rates = [g.previewRedeem(10**18) for g in gauges]
            time = mc.getCurrentBlockTimestamp()

        dt = time - t0
        t0 = time
        total_time += dt
        print(datetime.fromtimestamp(t0))

        for i in range(3):
            for u in list(users_to_check[i]):
                if lt_balances[i][u] == 0 and gauge_balances[i][u] == 0:
                    del lt_balances[i][u]
                    del gauge_balances[i][u]
                    users_to_check[i].remove(u)

        for i in range(3):
            for u, balance in lt_balances[i].items():
                tokens[u] += balance / BASE

        for i in range(3):
            for u, gbalance in gauge_balances[i].items():
                tokens[u] += gbalance * (redemption_rates[i] / BASE) / BASE

        total_tokens = sum(tokens.values())

        for u, balance in tokens.items():
            fraction_days[u] += balance * dt / 86400 / total_tokens

        print("    ", [(len(lb), sum(lb.values()) / BASE) for lb in lt_balances.values()], [(len(gb), sum(gb.values())/ BASE) for gb in gauge_balances.values()])
        print("    ", redemption_rates)
        print("    ", sum(tokens.values()))

    # pprint(fraction_days)
    print(sum(fraction_days.values()), total_time / 86400)

    # Normalize
    f_sum = sum(fraction_days.values())
    for u in fraction_days.keys():
        fraction_days[u] /= f_sum

    print(sum(fraction_days.values()))

    with open("split.json", "w") as f:
        json.dump(fraction_days, f)
