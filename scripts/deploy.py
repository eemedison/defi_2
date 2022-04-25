
from scripts.helpful_scripts import get_account, get_contract
from brownie import DappToken, TokenFarm, network, config
from web3 import Web3




KEPT_BALANCE = Web3.toWei(100, "ether")

def deploy_token_farm_and_dapp_token():
    account = get_account() ## get account helpful scripts'ten
    dapp_token = DappToken.deploy({"from": account})

    token_farm = TokenFarm.deploy(
        dapp_token.address, 
        {"from" : account},
        publish_source=config["networks"][network.show_active()]["verify"] ##network .yaml'dan geliyor
        )
    tx = dapp_token.transfer(
        token_farm.address, 
        dapp_token.totalSupply() - KEPT_BALANCE, 
        {"from": account}
        ) ## tüm dapp token balance'ı tokenfarm kontratına gönderdik

    tx.wait(1)
    #dapptoken, weth token, fau_token/dai (dai) (ers20faucet.com2dan verilebiliyor. biz bu dai'miş gibi davranacağız.)
    weth_token = get_contract("weth_token") #weth token contract MockWETH
    fau_token = get_contract("fau_token") #dai token contract MockDAI
    #dict ile yukarıda oluşturduğumuz boş kontratlara fiyat değeri eşleştiriyoruz. Eşitlemiyoruz çünkü dictionary!!!
    dict_of_allowed_tokens = {
        dapp_token: get_contract("dai_usd_price_feed"), #dai #get contract fonksiyonları helpful_scripts'ten
        fau_token: get_contract("dai_usd_price_feed"), #dai
        weth_token: get_contract("eth_usd_price_feed"), #eth
    }

    add_allowed_tokens(token_farm, dict_of_allowed_tokens, account)
    return token_farm, dapp_token

def add_allowed_tokens(token_farm, dict_of_allowed_token, account):
    for token in dict_of_allowed_token:
        add_tx = token_farm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = token_farm.setPriceFeedContract(
        token.address, 
        dict_of_allowed_token[token], 
        {"from": account}
        )
        set_tx.wait(1)
    return token_farm

def main():
    deploy_token_farm_and_dapp_token()