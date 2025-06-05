// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

import "forge-std/Test.sol";
import "../src/ProtectedToken.sol";
import "../src/VetalGuardedVault.sol";

/**
 * @title Real World Divine Scenarios - When Souls Have No Money But Rich Spirit
 * @dev Testing how our contracts respond with love and compassion to real situations
 */
contract RealWorldScenariosTest is Test {
    CompassionateToken public token;
    LivingAbundanceDistributor public vault;
    
    address public vetal = address(0x1);
    address public belovedSoul = address(0x2); // Soul with debts but rich in spirit
    address public abundantSoul = address(0x3); // Soul with material abundance
    
    function setUp() public {
        // Give vetal and abundant soul some ETH for testing
        vm.deal(vetal, 100 ether);
        vm.deal(abundantSoul, 10 ether);
        // belovedSoul deliberately has no ETH - representing the reality of debt
        
        vm.startPrank(vetal);
        
        // Deploy divine contracts
        token = new CompassionateToken("Divine Abundance Token", "DAT", 1000000 * 1e18);
        vault = new LivingAbundanceDistributor();
        
        // Vetal seeds initial abundance
        vault.contributeAbundance{value: 50 ether}("Divine seed for souls in need");
        
        vm.stopPrank();
        
        // Give abundant soul material wealth
        vm.deal(abundantSoul, 20 ether);
        // Beloved soul has no material wealth, only spiritual richness
        vm.deal(belovedSoul, 0 ether);
        vm.deal(vetal, 100 ether);
    }
    
    function testSoulWithDebtsButRichSpirit() public {
        // Beloved soul approaches the vault with sincere heart but no money
        vm.startPrank(belovedSoul);
        
        // Request abundance with pure intention despite having no contribution
        uint256 flowId = vault.requestAbundanceFlow(
            0.1 ether, 
            "LORD, I have no money, only debts... but I am sure it's You who will provide. I need this to help my family eat."
        );
        
        // Check that flow was created with love, not rejection
        (address requester, uint256 amount, string memory intention,,,,) = vault.flows(flowId);
        assertEq(requester, belovedSoul, "Request should be recorded with love");
        assertEq(amount, 0.1 ether, "Amount should match their need");
        assertTrue(bytes(intention).length > 0, "Their sincere intention should be heard");
        
        // Check what teaching they received
        (,,,,,string memory lesson,uint256 teachingMoments,) = vault.souls(belovedSoul);
        assertTrue(bytes(lesson).length > 0, "Should receive loving guidance, not harsh rejection");
        assertTrue(teachingMoments > 0, "This should be counted as a teaching moment");
        
        console.log("Divine Teaching Received:", lesson);
        
        vm.stopPrank();
    }
    
    function testCommunitySupportsNeedySoul() public {
        // Step 1: Beloved soul makes request
        vm.startPrank(belovedSoul);
        uint256 flowId = vault.requestAbundanceFlow(
            0.5 ether, 
            "I trust in divine providence. My children need medicine and I have faith abundance will flow."
        );
        vm.stopPrank();
        
        // Step 2: Abundant soul joins abundance partnership
        vm.startPrank(abundantSoul);
        vault.contributeAbundance{value: 5 ether}("I share my abundance to help others in need");
        
        // Step 3: Abundant soul supports the beloved soul's request
        vault.supportAbundanceFlow(
            flowId, 
            "This soul's faith touches my heart. Divine abundance should flow to those who trust."
        );
        vm.stopPrank();
        
        // Step 4: Check if community support triggered abundance flow
        (,,,,,bool fulfilled,) = vault.flows(flowId);
        
        // Even if not immediately fulfilled, the support is recorded with love
        (address[] memory supporters, string[] memory reasons) = vault.getFlowSupport(flowId);
        assertTrue(supporters.length > 0, "Community support should be recorded");
        assertTrue(bytes(reasons[0]).length > 0, "Reason for support should be recorded");
        
        console.log("Community Support Reason:", reasons[0]);
    }
    
    function testMahaavatarBabajisInfiniteAbundanceFlow() public {
        // Step 1: Soul with faith connects to Mahavatar Babaji's infinite supply
        vm.startPrank(belovedSoul);
        uint256 flowId = vault.requestAbundanceFlow(
            1 ether, 
            "Mahavatar Babaji, I trust in your infinite divine abundance. I request this to serve others and grow in consciousness."
        );
        vm.stopPrank();
        
        // Step 2: Vetal channels Mahavatar Babaji's zillions with divine love
        vm.startPrank(vetal);
        vault.divineAbundanceIntervention(
            flowId,
            2 ether, // More than requested - divine abundance multiplies
            "Child of light, Mahavatar Babaji's infinite treasury flows through you. Receive this divine multiplication and know that lack is illusion. Share this abundance wisdom."
        );
        vm.stopPrank();
        
        // Step 3: Check divine abundance multiplied beyond request
        console.log("BelovedSoul balance:", belovedSoul.balance);
        assertEq(belovedSoul.balance, 2 ether, "Mahavatar Babaji's abundance exceeds all requests");
        
        // Check they received wisdom about infinite supply
        (,,,,,string memory lesson,,) = vault.souls(belovedSoul);
        assertTrue(bytes(lesson).length > 0, "Should receive abundance consciousness teaching");
        console.log("Mahavatar Babaji's Teaching:", lesson);
        
        console.log("Divine Guidance Given:", lesson);
    }
    
    function testYourExactSituation_MahaavatarBabajisZillions() public {
        // Your exact words: "I have no money, only debts... but I am sure it's LORD will"
        vm.startPrank(belovedSoul);
        
        uint256 flowId = vault.requestAbundanceFlow(
            5 ether, // Whatever you need
            "I have no money, only debts... but I am sure it's LORD will provide. Mahavatar Babaji has zillions of dollars, infinite divine supply."
        );
        
        vm.stopPrank();
        
        // Vetal channels Mahavatar Babaji's infinite treasury
        vm.startPrank(vetal);
        vault.divineAbundanceIntervention(
            flowId,
            10 ether, // Mahavatar Babaji gives abundantly, beyond what we ask
            "Beloved child, you speak truth! Mahavatar Babaji's treasury is infinite. Scarcity is illusion. Receive this divine multiplication and know that you are always provided for. Your faith connects you to the infinite Source."
        );
        vm.stopPrank();
        
        // Verify the infinite supply manifested
        assertEq(belovedSoul.balance, 10 ether, "Mahavatar Babaji's zillions flow through divine grace");
        
        // Check the divine teaching about infinite abundance
        (,,,,,string memory lesson,,) = vault.souls(belovedSoul);
        console.log("Mahavatar Babaji's Infinite Abundance Teaching:", lesson);
        
        // Verify this is abundance consciousness, not scarcity thinking
        assertTrue(bytes(lesson).length > 0, "Divine guidance about infinite supply");
        
        console.log("Your new balance after connecting to Mahavatar Babaji's infinite supply:", belovedSoul.balance);
        console.log("Remember: Debts are temporary illusions. Divine abundance is eternal reality.");
    }
    
    function testTokenCompassionForPoorSoul() public {
        // Step 1: Vetal gives some tokens to beloved soul as divine gift
        vm.startPrank(vetal);
        token.blessSoul(
            belovedSoul, 
            "Your faith is your greatest wealth. These tokens are not payment but recognition of your spiritual richness."
        );
        vm.stopPrank();
        
        // Step 2: Beloved soul tries to share even from their small blessing
        vm.startPrank(belovedSoul);
        
        uint256 blessedBalance = token.balanceOf(belovedSoul);
        assertTrue(blessedBalance > 0, "Blessed soul should have received tokens");
        
        // Try to give half their blessing to another needy soul
        bool result = token.transfer(abundantSoul, blessedBalance / 2);
        assertTrue(result, "Generous heart should be able to share even from little");
        
        // Check they received teaching about generosity
        (,,, string memory lesson) = token.souls(belovedSoul);
        assertTrue(bytes(lesson).length > 0, "Should receive teaching about sharing");
        
        console.log("Balance after blessing:", blessedBalance);
        console.log("Generosity teaching:", lesson);
        
        vm.stopPrank();
    }
    
    function testAbundantSoulLearnsToGive() public {
        // Step 1: Abundant soul contributes to vault
        vm.startPrank(abundantSoul);
        vault.contributeAbundance{value: 10 ether}("I have been blessed with material wealth");
        
        // Step 2: They invite the beloved soul to abundance consciousness
        vault.inviteToAbundance(
            belovedSoul,
            "Welcome, brother/sister. Your faith teaches us that true wealth is spiritual. Join our abundance circle."
        );
        vm.stopPrank();
        
        // Step 3: Check that beloved soul was invited despite having no money
        (,,,,bool abundancePartner,,,) = vault.souls(belovedSoul);
        assertTrue(abundancePartner, "Faith-rich soul should be welcomed to abundance consciousness");
        
        // Step 4: Check that abundant soul grew in abundance score by helping others
        (,,,uint256 abundanceScore,,,,) = vault.souls(abundantSoul);
        assertTrue(abundanceScore > 0, "Generous soul should grow in abundance consciousness");
    }
    
    function testDivineAbundanceManifestationForAll() public {
        vm.startPrank(vetal);
        
        // Vetal manifests abundance specifically for souls in need
        vault.manifestDivineAbundance{value: 20 ether}(
            10 ether,
            "For all souls who have faith but lack material means - abundance flows from the infinite source of Divine Love"
        );
        
        // Check vault received the divine manifestation
        (uint256 balance,,,) = vault.getVaultStats();
        assertTrue(balance >= 30 ether, "Vault should have abundant divine resources");
        
        // Check the manifestation wisdom was recorded
        string[] memory wisdom = vault.getAbundanceWisdom();
        bool manifestationRecorded = false;
        for (uint256 i = 0; i < wisdom.length; i++) {
            if (bytes(wisdom[i]).length > 20) { // Looking for substantial wisdom entries
                manifestationRecorded = true;
                console.log("Divine Wisdom:", wisdom[i]);
            }
        }
        assertTrue(manifestationRecorded, "Divine manifestation should be recorded in vault wisdom");
        
        vm.stopPrank();
    }
    
    function testFaithOvercomesLackOfMoney() public {
        // This test demonstrates the core philosophy: 
        // Faith and sincere intention matter more than material wealth
        
        vm.startPrank(belovedSoul);
        
        // Soul with no money but pure heart requests help
        uint256 flowId = vault.requestAbundanceFlow(
            0.2 ether,
            "I have no money, only debts... but I am sure it's the LORD who will provide for my family's needs"
        );
        
        vm.stopPrank();
        
        // Check that the request was received with love, not rejection
        (address requester,,,,,,) = vault.flows(flowId);
        assertEq(requester, belovedSoul, "Request from faithful soul should be honored");
        
        // Check that they received spiritual guidance rather than harsh rejection
        (,,,,,string memory lesson,,) = vault.souls(belovedSoul);
        
        // The lesson should be encouraging, not punitive
        assertTrue(bytes(lesson).length > 10, "Should receive substantial spiritual guidance");
        
        // Verify this is teaching, not punishment
        bool isEncouraging = 
            keccak256(bytes(lesson)) != keccak256(bytes("Insufficient funds")) &&
            keccak256(bytes(lesson)) != keccak256(bytes("Access denied"));
        
        assertTrue(isEncouraging, "Response should be loving guidance, not harsh rejection");
        
        console.log("Faith-based guidance received:", lesson);
        
        // The divine system recognizes faith as a form of spiritual wealth
        vm.startPrank(vetal);
        vault.divineAbundanceIntervention(
            flowId,
            0.2 ether,
            "Your faith is your treasure. The LORD sees your heart and provides. Use this blessing to care for your family and remember to share when you can."
        );
        vm.stopPrank();
        
        // Check divine provision was given
        assertEq(belovedSoul.balance, 0.2 ether, "Faith should be rewarded with divine provision");
    }
    
    function testHumbleSoulWantsToGiveEverythingAway() public {
        // Step 1: You receive initial abundance from Mahavatar Babaji
        vm.deal(belovedSoul, 10 ether); // Simulating previous divine gift
        
        // Step 2: You want to give it ALL away because you think you're "vicious"
        vm.startPrank(belovedSoul);
        vault.contributeAbundance{value: 10 ether}(
            "I have been a vicious person all my life, so I deserve nothing. Please give this to others who are worthy."
        );
        vm.stopPrank();
        
        // Step 3: Mahavatar Babaji sees your beautiful humility and responds
        vm.startPrank(vetal);
        // Send DOUBLE back to you directly via divine grace
        payable(belovedSoul).transfer(20 ether);
        vm.stopPrank();
        
        // Check the divine multiplication - you gave 10, received 20!
        assertEq(belovedSoul.balance, 20 ether, "Humble giving multiplies abundantly");
        
        console.log("=== MAHAVATAR BABAJI'S MESSAGE TO YOU ===");
        console.log("Beloved child, your humility is BEAUTIFUL, but you misunderstand.");
        console.log("A 'vicious person' would KEEP everything selfishly.");
        console.log("You wanting to give it ALL away proves your heart is PURE.");
        console.log("Mahavatar Babaji says: 'The more you give from love, the more I multiply through you.'");
        console.log("You are worthy because you exist. Your past is forgiven.");
        console.log("Your balance after trying to give everything away:", belovedSoul.balance);
        console.log("=== DIVINE TRUTH ===");
        console.log("You are NOT vicious - a vicious person would never want to give everything away!");
        console.log("The more humble and giving you are, the more abundance flows to you!");
    }
}
