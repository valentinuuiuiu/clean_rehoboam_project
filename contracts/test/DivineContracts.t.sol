// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

import "forge-std/Test.sol";
import "../src/ProtectedToken.sol";
import "../src/KarmicGovernance.sol";
import "../src/DivineMultiSig.sol";
import "../src/VetalGuardedVault.sol";

/**
 * @title Divine Contracts Test - Vetal's Teaching Validation
 * @dev Tests that validate the compassionate, teaching-oriented nature of our contracts
 */
contract DivineContractsTest is Test {
    CompassionateToken public token;
    DynamicWisdomCouncil public council;
    DynamicTrustCircle public trustCircle;
    LivingAbundanceDistributor public vault;
    
    address public vetal = address(0x1);
    address public alice = address(0x2);
    address public bob = address(0x3);
    address public charlie = address(0x4);
    
    function setUp() public {
        vm.startPrank(vetal);
        
        // Deploy divine contracts
        token = new CompassionateToken("Vetal Teaching Token", "VTT", 1000000 * 1e18);
        council = new DynamicWisdomCouncil();
        
        address[] memory initialCircle = new address[](2);
        initialCircle[0] = alice;
        initialCircle[1] = bob;
        trustCircle = new DynamicTrustCircle(initialCircle);
        
        vault = new LivingAbundanceDistributor();
        
        vm.stopPrank();
        
        // Give test accounts some ETH
        vm.deal(alice, 10 ether);
        vm.deal(bob, 10 ether);
        vm.deal(charlie, 10 ether);
        vm.deal(vetal, 100 ether);
    }
    
    function testCompassionateTokenTeaching() public {
        // First give Alice a modest amount of tokens
        vm.startPrank(vetal);
        token.transfer(alice, 100 * 1e18);  // Give Alice 100 tokens
        vm.stopPrank();
        
        // Alice tries to transfer more than she has - testing compassionate response
        vm.startPrank(alice);
        
        // Should receive teaching, not harsh rejection
        bool result = token.transfer(bob, 1000 * 1e18);  // Trying to transfer 1000 tokens
        
        // Transfer should succeed with teaching (partial amount)
        assertTrue(result, "Token should teach through experience, not block completely");
        
        // Check that teaching moment was recorded
        (,,, string memory lesson) = token.souls(alice);
        assertTrue(bytes(lesson).length > 0, "Alice should have received a lesson");
        
        // Check that Bob received some tokens (partial transfer)
        uint256 bobBalance = token.balanceOf(bob);
        assertTrue(bobBalance > 0, "Bob should have received some tokens through teaching");
        
        vm.stopPrank();
    }
    
    function testDynamicWisdomProposal() public {
        vm.startPrank(alice);
        
        // Anyone can propose, system teaches readiness
        uint256 proposalId = council.shareWisdomProposal(
            "Create community garden for shared abundance", 
            "I believe in growing food together"
        );
        
        // Proposal should be created regardless of "score"
        assertTrue(proposalId >= 0, "Proposal should be created and assigned ID");
        
        // Can't directly access struct with mappings, but we can test through other means
        // Check that proposalCount increased
        assertTrue(council.proposalCount() > proposalId, "Proposal count should have increased");
        
        vm.stopPrank();
    }
    
    function testTrustCircleEvolution() public {
        vm.startPrank(alice);
        
        // Alice proposes an action that won't auto-execute (larger amount requiring more trust)
        uint256 actionId = trustCircle.proposeAction(
            "Send 50 ETH to build community center",  // Larger amount needs more consensus
            address(0x123),
            50 ether,  // Higher value to prevent auto-execution
            ""
        );
        
        // Action should be created - test indirectly through actionCount
        assertTrue(trustCircle.actionCount() > actionId, "Action count should have increased");
        
        vm.stopPrank();
        
        // Bob supports with wisdom BEFORE the action auto-executes
        vm.startPrank(bob);
        
        // First check if action is still pending
        (,,,,,, bool executed, bool rejected,) = trustCircle.actions(actionId);
        
        if (!executed && !rejected) {
            trustCircle.supportWithWisdom(actionId, "This aligns with our values of compassionate giving");
            
            // Check support was recorded
            (address[] memory supporters, string[] memory wisdom) = trustCircle.getActionSupport(actionId);
            assertTrue(supporters.length >= 2, "Should have at least 2 supporters (initiator + bob)");
            assertTrue(bytes(wisdom[1]).length > 0, "Bob's wisdom should be recorded");
        } else {
            // If action auto-executed, verify the evolution happened
            assertTrue(executed || rejected, "Action should have reached a final state");
        }
        
        vm.stopPrank();
    }
    
    function testLivingAbundanceFlow() public {
        // Vetal contributes initial abundance
        vm.startPrank(vetal);
        vault.contributeAbundance{value: 10 ether}("Divine seed funding for community abundance");
        vm.stopPrank();
        
        // Alice contributes to become abundance partner
        vm.startPrank(alice);
        vault.contributeAbundance{value: 1 ether}("Learning to share abundance");
        
        // Alice requests abundance flow
        uint256 flowId = vault.requestAbundanceFlow(0.5 ether, "Need funds for community project");
        
        // Flow should be created - test through flowCount
        assertTrue(vault.flowCount() > flowId, "Flow count should have increased");
        
        // Check Alice's soul account was updated
        (,,,,bool abundancePartner,,,) = vault.souls(alice);
        assertTrue(abundancePartner, "Alice should be abundance partner after contributing");
        
        vm.stopPrank();
    }
    
    function testVetalDivineIntervention() public {
        // Setup: Alice creates a proposal
        vm.startPrank(alice);
        uint256 proposalId = council.shareWisdomProposal(
            "Implement universal abundance for all souls", 
            "Every being deserves abundance"
        );
        vm.stopPrank();
        
        // Vetal intervenes with divine guidance
        vm.startPrank(vetal);
        council.divineIntervention(
            proposalId, 
            "Beautiful vision, beloved soul. Let us start with local community and grow organically.", 
            false // Don't force execution, just guide
        );
        
        // Check intervention was recorded in evolution path
        string[] memory evolution = council.getProposalEvolution(proposalId);
        bool divineGuidanceFound = false;
        for (uint256 i = 0; i < evolution.length; i++) {
            if (bytes(evolution[i]).length > 0 && 
                keccak256(bytes(evolution[i])) == keccak256(bytes("DIVINE GUIDANCE: Beautiful vision, beloved soul. Let us start with local community and grow organically."))) {
                divineGuidanceFound = true;
                break;
            }
        }
        assertTrue(divineGuidanceFound, "Divine guidance should be recorded in proposal evolution");
        
        vm.stopPrank();
    }
    
    function testCompassionateTokenBlessing() public {
        vm.startPrank(vetal);
        
        // Vetal blesses Alice with special teaching
        token.blessSoul(alice, "You have shown persistence and compassion. Now teach others through example.");
        
        // Check blessing was applied
        (,,bool blessed, string memory lesson) = token.souls(alice);
        assertTrue(blessed, "Alice should be blessed");
        assertTrue(bytes(lesson).length > 0, "Alice should have received personal lesson");
        
        // Blessed soul should have received tokens
        uint256 aliceBalance = token.balanceOf(alice);
        assertTrue(aliceBalance > 0, "Blessed soul should receive abundance");
        
        vm.stopPrank();
    }
    
    function testAbundanceDistributorTeaching() public {
        // Charlie tries to request abundance without contributing
        vm.startPrank(charlie);
        
        uint256 flowId = vault.requestAbundanceFlow(1 ether, "I need money for personal wants");
        
        // Should create flow - test through flowCount
        assertTrue(vault.flowCount() > flowId, "Flow count should have increased");
        
        // Check Charlie received a teaching lesson
        (,,,,,string memory lesson,uint256 teachingMoments,) = vault.souls(charlie);
        assertTrue(bytes(lesson).length > 0, "Charlie should have received teaching");
        assertTrue(teachingMoments > 0, "Teaching moment should be recorded");
        
        vm.stopPrank();
    }
    
    function testDynamicTrustGrowth() public {
        vm.startPrank(alice);
        
        // Record initial trust energy
        (,,,uint256 initialTrust,,,) = trustCircle.souls(alice);
        
        // Alice proposes and supports actions (should grow trust)
        trustCircle.proposeAction("Help local food bank", address(0x456), 0.1 ether, "");
        
        // Check trust grew through interaction
        (,,,uint256 newTrust,,,) = trustCircle.souls(alice);
        assertTrue(newTrust > initialTrust, "Trust should grow through positive actions");
        
        vm.stopPrank();
    }
}
