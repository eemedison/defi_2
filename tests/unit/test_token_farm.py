
   
from scripts.deploy import deploy_token_farm_and_dapp_token, KEPT_BALANCE
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    INITIAL_PRICE_FEED_VALUE,
    get_account,
    get_contract,
)
from brownie import network, exceptions
import pytest
from web3 import Web3

def test_set_price_feed_contract():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    #token_farm.addAllowedTokens(dapp_token.address, {"from": account})
    price_feed_address = get_contract("eth_usd_price_feed")
    token_farm.setPriceFeedContract( #👉🏼 dappToken fiyatını set ettik. 
        dapp_token.address,
        price_feed_address,
        {"from": account}
    )
    # Assert
    #assert token_farm.allowedTokens(0) == dapp_token.address
    assert token_farm.tokenPriceFeedMapping(dapp_token.address) == price_feed_address
    with pytest.raises(exceptions.VirtualMachineError):
        #token_farm.addAllowedTokens(dapp_token.address, {"from": non_owner})
        token_farm.setPriceFeedContract(dapp_token.address,price_feed_address, {"from": non_owner})

def test_stake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    dapp_token.approve(token_farm.address, amount_staked, {"from": account}) #to, amount, from
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from" : account})
    assert(
        token_farm.stakingBalance(dapp_token.address, account.address) == amount_staked
    )
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address
    return token_farm, dapp_token

def test_issue_tokens(amount_staked): #amount_staked = 1 ETH
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked) # 1 ETH
    starting_balance = dapp_token.balanceOf(account.address)#dapp token bir üst satırdan geliyor stake edilen dapp token bundan account'da ne kadar var.
    # Act
    token_farm.issueTokens({"from": account})

    # we are staking 1 dapp token == in price to 1 ETH
    # soo ... we should get 2000 dapp tokens in reward
    # 1 ETH = 2000 USD

    # Assert
    assert (
        dapp_token.balanceOf(account.address)
        == starting_balance + INITIAL_PRICE_FEED_VALUE #dapp token stake ettik.
        # Bu test için 1ETH'lık dapp token stake ettik. amount_staked = 1 ETH
        # 1 ETH = 2000 USD olduğundan yaklaşık 2000 dapp stake etmiş olduk.
        # Bu starting balance'ımız. INITIAL Price Feed değeri de 2000 idi.
        # Biz adama reward verdiğimizde adamda hem stake ettiği (starting balance)
        # hem de reward aldığı initial_price_feed_value (2000 dapp token) olacak.
    )