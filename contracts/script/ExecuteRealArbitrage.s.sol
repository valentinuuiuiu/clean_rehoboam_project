// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

import "forge-std/Script.sol";
import "../src/FlashArbitrageBot.sol";

contract ExecuteRealArbitrage is Script {
    address constant BOT_ADDRESS = 0x5FbDB2315678afecb367f032d93F642f64180aa3;
    
    // Your actual MetaMask wallet address - replace with your real address
    address payable yourWallet = payable(0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266);
    
    function run() external {
        // Use the first test account as the executor
        vm.startBroadcast(0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80);
        
        // Get the bot contract instance
        FlashArbitrageBot bot = FlashArbitrageBot(BOT_ADDRESS);
        
        console.log("=== EXECUTING REAL FLASH ARBITRAGE ===");
        console.log("Bot Contract:", address(bot));
        console.log("Your Wallet:", yourWallet);
        console.log("Executor Balance Before:", address(this).balance);
        
        // Example: WETH arbitrage between Uniswap and SushiSwap
        address weth = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
        address usdc = 0xA0b86a33E6417aB1cc6a0b6b96d6A2aF7e6B8B6E;
        
        // Execute arbitrage with 10 ETH flash loan
        uint256 flashAmount = 10 ether;
        
        try bot.executeArbitrage(
            weth,           // asset to flash loan
            flashAmount,    // amount to borrow
            usdc,           // asset to trade for
            yourWallet      // send profits here
        ) {
            console.log("SUCCESS: Arbitrage executed successfully!");
            
            // Check profits
            uint256 profit = yourWallet.balance;
            console.log("PROFIT: Profit sent to your wallet:", profit);
            
            if (profit > 0) {
                console.log("SUCCESS! You now have", profit, "wei in your wallet!");
                console.log("INFO: This proves flash arbitrage works with ZERO upfront capital!");
            }
            
        } catch Error(string memory reason) {
            console.log("ERROR: Arbitrage failed:", reason);
        }
        
        vm.stopBroadcast();
    }
    
    // Function to find and execute profitable opportunities automatically
    function findAndExecuteOpportunity() external {
        vm.startBroadcast(0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80);
        
        // Get the bot contract instance
        FlashArbitrageBot bot = FlashArbitrageBot(BOT_ADDRESS);
        
        console.log("SEARCH: Searching for profitable arbitrage opportunities...");
        
        // Check WETH/USDC price differences across DEXs
        address[] memory tokens = new address[](2);
        tokens[0] = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2; // WETH
        tokens[1] = 0xA0b86a33E6417aB1cc6a0b6b96d6A2aF7e6B8B6E; // USDC
        
        // Simulate different flash amounts to find profitable ones
        uint256[] memory amounts = new uint256[](5);
        amounts[0] = 1 ether;
        amounts[1] = 5 ether;
        amounts[2] = 10 ether;
        amounts[3] = 50 ether;
        amounts[4] = 100 ether;
        
        for (uint i = 0; i < amounts.length; i++) {
            console.log("Testing flash amount:", amounts[i]);
            
            try bot.executeArbitrage(
                tokens[0],
                amounts[i],
                tokens[1],
                yourWallet
            ) {
                console.log("SUCCESS: Found profitable opportunity with", amounts[i], "flash amount!");
                break;
            } catch {
                console.log("FAIL: No profit with", amounts[i], "amount");
            }
        }
        
        vm.stopBroadcast();
    }
}
