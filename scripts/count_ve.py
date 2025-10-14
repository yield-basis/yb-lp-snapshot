from brownie import config
from brownie import Contract
import re


config['autofetch_sources'] = True

ARAGON = "0xE478de485ad2fe566d49342Cbd03E49ed7DB3356"
VE = "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2"
votes = [1206, 1213, 1222]
re_addr = re.compile(r'(0x[a-fA-F0-9]{40})')


def main():
    aragon = Contract(ARAGON)
    ve = Contract(VE)
    for vid in votes:
        with open(f've/{vid}.html', 'r') as f:
            text = f.read()
        addrs = list(set(re_addr.findall(text)))
        print(vid, len(addrs))
        vote_state = aragon.getVote(vid)
        block = vote_state[3]
        relevant_ve = sum([ve.balanceOfAt(addr, block) * (aragon.getVoterState(vid, addr) in [1, 3]) for addr in addrs])
        print(relevant_ve)
