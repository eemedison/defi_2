import pytest
from web3 import Web3

@pytest.fixture ##fixture oluşturmayı öğrendik

def amount_staked():
    return Web3.toWei(1, "ether")