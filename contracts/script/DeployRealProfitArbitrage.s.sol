// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/RealProfitFlashArbitrage.sol";

contract DeployRealProfitArbitrage is Script {
    address private constant YOUR_WALLET = 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8;
    
    function run() external {
        console.log("DEPLOYING FLASH ARBITRAGE CONTRACT");
        console.log("Profit destination:", YOUR_WALLET);
        
        vm.startBroadcast();
        
        RealProfitFlashArbitrage arbitrageContract = new RealProfitFlashArbitrage();
        
        vm.stopBroadcast();
        
        console.log("SUCCESS! Contract deployed at:", address(arbitrageContract));
        console.log("ALL PROFITS GO TO:", YOUR_WALLET);
    }
}
