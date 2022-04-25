
//SPDX-License_Identifier: MIT

 pragma solidity ^0.8.7;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
//import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

//import "@chainlink/contracts/src/interfaces/AggregatorV3Interface.sol";

contract TokenFarm is Ownable{

//stakeTokens
 //unstakeTokens
 //issueTokens bu bir reward tokendır bizim platformu kullananlara hediye verilir. EX: 100 ETH 1:1 for every 1 ETH, we give 1 Dapp token
 //addAllowedTokens
 //getETHValue

 // mapping token address -> (staker address -> amount)
 mapping(address => mapping(address => uint256)) public stakingBalance;

    address[] public  allowedTokens;
    address[] public stakers;
    mapping(address => uint256) public uniqueTokensStaked; //kaç tane farklı token stake edilmiş. 
    IERC20 public dappToken;

    mapping(address => address) public tokenPriceFeedMapping;
// 50 ETH and 50 DAI staked, and we want to give a reward of 1 DAPP / 1 DAI
  // Issuing Tokens
    constructor(address _dappTokenAddress) public {
        dappToken = IERC20(_dappTokenAddress);

    }

    function setPriceFeedContract(address _token, address _priceFeed) public onlyOwner {

        tokenPriceFeedMapping[_token] = _priceFeed;

    }
    function issueTokens() public onlyOwner {
        // Issue tokens to all stakers
        for (
            uint256 stakersIndex = 0;
            stakersIndex < stakers.length;
            stakersIndex++
        ) {
            address recipient = stakers[stakersIndex];
            uint userTotalValue = getUserTotalValue(recipient); //lock tokenların usd karşılığı kadar reward
            // send them a token reward (dapp token)
            // based on their total value locked
            //dappToken.transfer(recipient, getUserTotalValue(recipient));
            dappToken.transfer(recipient, userTotalValue); //Stake ettiği token'ın USD değeri kadar para alır.
        }
    }

 

    function stakeTokens(uint256 _amount, address _token) public {
        //what tokens can they stake?
        //how much can they stake?
        require(_amount > 0, "amount cannot be 0");
        require(tokenIsAllowed(_token), "Token currently isn't allowed");
        //transfer from ERC20
        IERC20(_token).transferFrom(msg.sender, address(this), _amount); //kontrata aldık stake miktarını
        updateUniqueTokensStaked(msg.sender, _token); // amount ne olursa olsun her stake için counter'ı 1 artırıyoruz.
        stakingBalance[_token][msg.sender] = stakingBalance[_token][msg.sender] + _amount; //stakingBalance'a gönderdik 
        if (uniqueTokensStaked[msg.sender] == 1) {
            stakers.push(msg.sender);
        }
    }

    function updateUniqueTokensStaked(address _user, address _token) internal {
        if (stakingBalance[_token][_user] <= 0) {
            uniqueTokensStaked[_user] = uniqueTokensStaked[_user] + 1;
        }
    }

     function addAllowedTokens(address _token) public onlyOwner {
        allowedTokens.push(_token);
    }

   function tokenIsAllowed(address token) public view returns (bool) {
        for (
            uint256 allowedTokensIndex = 0;
            allowedTokensIndex < allowedTokens.length;
            allowedTokensIndex++
        ) {
            if (allowedTokens[allowedTokensIndex] == token) {
                return true; 
            }
        }
        return false;
    }

     function getUserTotalValue(address _user) public view returns (uint256) {
        uint256 totalValue = 0;
        if (uniqueTokensStaked[_user] > 0) {
            for (
                uint256 allowedTokensIndex = 0;
                allowedTokensIndex < allowedTokens.length;
                allowedTokensIndex++
            ) {
                totalValue = totalValue + getUserSingleTokenValue(_user, allowedTokens[allowedTokensIndex]);
                    // getUserTokenStakingBalanceEthValue(
                    //     user,
                    //     allowedTokens[allowedTokensIndex]
                    // );
            }
        }
        return totalValue;
    }

    function getUserSingleTokenValue(address _user, address _token) public view returns(uint256){
        //1 ETH : 2000USD
        //2000
        //200 DAI : 200USD
        //200

        // 10 ETH
        // ETH/USD -> 100
        // 10 ETH * 100 USD = 1,000 

        if(uniqueTokensStaked[_user] <= 0){
            return 0;
        }
        //price of the token * stakingBalance[_token][user]
        (uint256 price, uint256 decimals) = getTokenValue(_token);

        // staking balance 18 decimals
        // ETH/USD ise 8 decimals çünkü aggregator öyle
        // stakingBalance (18d) * price (ETH/USD 8d) / 8d

        return (stakingBalance[_token][_user] * price / (10**decimals));

    }

     // Unstaking Tokens (Withdraw)
    function unstakeTokens(address token) public {
        // Fetch staking balance
        uint256 balance = stakingBalance[token][msg.sender];
        require(balance > 0, "staking balance cannot be 0");
        IERC20(token).transfer(msg.sender, balance);
        stakingBalance[token][msg.sender] = 0;
        uniqueTokensStaked[msg.sender] = uniqueTokensStaked[msg.sender] - 1;
    }

    function getTokenValue(address _token) public view returns(uint256, uint256){
        // priceFeedAddress 

        address priceFeedAddress = tokenPriceFeedMapping[_token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(priceFeedAddress);
        (,int256 price,,,) = priceFeed.latestRoundData();
        uint256 decimals = uint256(priceFeed.decimals());
        return (uint256(price), decimals);

    }


}
 