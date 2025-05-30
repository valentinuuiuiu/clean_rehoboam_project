// Validator: Vetal Shabar Raksa
// This contract represents a dynamic trust circle that evolves with its members.
// Improvements and optimizations are encouraged to enhance functionality and security.
// Current focus: Ensuring compassionate governance and teaching-oriented interactions.
// Validator: Vetal Shabar Raksa
// This contract represents a dynamic trust circle that evolves with its members.
// Improvements and optimizations are encouraged to enhance functionality and security.
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

/**
 * @title DynamicTrustCircle - Living Multi-Sig That Evolves
 * @dev A trust circle that adapts, teaches, and grows organically
 * No rigid requirements - only dynamic trust that responds to collective wisdom
 */
contract DynamicTrustCircle {
    
    struct TrustSoul {
        bool isTrusted;              // Currently in the circle
        uint256 joinedAt;            // When they entered the circle
        uint256 trustEnergy;         // Dynamic trust level
        uint256 actionsInitiated;    // How often they propose
        uint256 actionsSupported;    // How often they support others
        string currentRole;          // Their evolving role in the circle
        address sponsor;             // Who brought them into the circle
    }
    
    struct CircleAction {
        string essence;              // What this action aims to achieve
        address initiator;           // Who proposed it
        uint256 createdAt;          // When it was proposed
        bytes callData;             // The actual transaction data
        address target;             // Where to send the transaction
        uint256 value;              // ETH value to send
        mapping(address => bool) hasSupported;  // Who supports this
        mapping(address => string) supportWisdom; // Why they support
        address[] supporters;        // List of supporters
        bool executed;              // Has it been completed
        bool rejected;              // Has it been rejected
        string[] evolutionPath;     // How the action evolved
        uint256 trustEnergyRequired; // Dynamic trust threshold
    }
    
    mapping(address => TrustSoul) public souls;
    mapping(uint256 => CircleAction) public actions;
    uint256 public actionCount;
    address public vetalGuardian;
    address[] public trustCircle;
    
    string[] public circleWisdom; // Lessons learned by the circle
    uint256 public totalTrustEnergy; // Collective trust in the circle
    
    event SoulJoinedCircle(address indexed soul, address indexed sponsor, string role);
    event SoulEvolvedRole(address indexed soul, string newRole, string reason);
    event ActionProposed(uint256 indexed actionId, address indexed initiator, string essence);
    event TrustGiven(uint256 indexed actionId, address indexed supporter, string wisdom);
    event ActionEvolved(uint256 indexed actionId, string evolution);
    event ActionExecuted(uint256 indexed actionId, bool success, string result);
    event CircleGrew(uint256 newSize, uint256 totalTrustEnergy);
    event DivineGuidance(address indexed vetal, string guidance, uint256 actionId);
    
    modifier onlyTrustedSoul() {
        require(souls[msg.sender].isTrusted, "Not in the trust circle");
        _;
    }
    
    modifier withTrustEvolution() {
        if (souls[msg.sender].isTrusted) {
            souls[msg.sender].trustEnergy += 1; // Small growth with each interaction
        }
        _;
    }
    
    constructor(address[] memory initialCircle) {
        vetalGuardian = msg.sender;
        
        // Initialize the founding circle
        for (uint256 i = 0; i < initialCircle.length; i++) {
            address soul = initialCircle[i];
            souls[soul] = TrustSoul({
                isTrusted: true,
                joinedAt: block.timestamp,
                trustEnergy: 100,
                actionsInitiated: 0,
                actionsSupported: 0,
                currentRole: i == 0 ? "Founding Guardian" : "Founding Member",
                sponsor: vetalGuardian
            });
            trustCircle.push(soul);
            totalTrustEnergy += 100;
        }
        
        // Vetal has special divine status
        souls[vetalGuardian] = TrustSoul({
            isTrusted: true,
            joinedAt: block.timestamp,
            trustEnergy: 1000,
            actionsInitiated: 0,
            actionsSupported: 0,
            currentRole: "Divine Guardian",
            sponsor: address(0)
        });
        
        if (!_isInCircle(vetalGuardian)) {
            trustCircle.push(vetalGuardian);
            totalTrustEnergy += 1000;
        }
        
        circleWisdom.push("Trust is earned through action, not inherited through position");
        circleWisdom.push("Every soul has the potential to contribute to the collective good");
        circleWisdom.push("Decisions emerge from wisdom, not power");
    }
    
    /**
     * @dev Propose an action to the circle - dynamic trust threshold
     */
    function proposeAction(
        string memory essence,
        address target,
        uint256 value,
        bytes memory callData
    ) external onlyTrustedSoul withTrustEvolution returns (uint256) {
        uint256 actionId = actionCount++;
        CircleAction storage action = actions[actionId];
        
        action.essence = essence;
        action.initiator = msg.sender;
        action.createdAt = block.timestamp;
        action.target = target;
        action.value = value;
        action.callData = callData;
        
        // Dynamic trust threshold based on action complexity and initiator's history
        action.trustEnergyRequired = _calculateRequiredTrust(msg.sender, value, callData);
        
        // Initiator automatically supports their own proposal
        action.supporters.push(msg.sender);
        action.hasSupported[msg.sender] = true;
        action.supportWisdom[msg.sender] = "I believe in this action and take responsibility for its outcome";
        
        action.evolutionPath.push(string(abi.encodePacked("Proposed by ", souls[msg.sender].currentRole)));
        
        souls[msg.sender].actionsInitiated++;
        
        emit ActionProposed(actionId, msg.sender, essence);
        
        // Check if it can execute immediately (for simple actions by highly trusted souls)
        _checkForExecution(actionId);
        
        return actionId;
    }
    
    /**
     * @dev Dynamic trust calculation - out-of-the-box thinking
     */
    function _calculateRequiredTrust(address initiator, uint256 value, bytes memory callData) 
        private 
        view 
        returns (uint256) 
    {
        uint256 baseTrust = 50; // Minimum trust required
        
        // Higher value = more trust needed
        if (value > 1 ether) baseTrust += 100;
        if (value > 10 ether) baseTrust += 200;
        
        // Complex calls need more trust
        if (callData.length > 100) baseTrust += 50;
        if (callData.length > 500) baseTrust += 100;
        
        // Experienced souls need less initial trust
        uint256 initiatorExperience = souls[initiator].actionsInitiated + souls[initiator].actionsSupported;
        if (initiatorExperience >= 10) baseTrust -= 30;
        if (initiatorExperience >= 20) baseTrust -= 50;
        
        // High trust souls get reduced requirements
        if (souls[initiator].trustEnergy >= 200) baseTrust -= 50;
        if (souls[initiator].trustEnergy >= 500) baseTrust -= 100;
        
        // Ensure minimum threshold
        if (baseTrust < 20) baseTrust = 20;
        
        return baseTrust;
    }
    
    /**
     * @dev Support an action with wisdom - not just a signature
     */
    function supportWithWisdom(uint256 actionId, string memory wisdom) 
        external 
        onlyTrustedSoul 
        withTrustEvolution 
    {
        require(actionId < actionCount, "Action does not exist");
        CircleAction storage action = actions[actionId];
        require(!action.executed && !action.rejected, "Action already finalized");
        require(!action.hasSupported[msg.sender], "Already supported this action");
        
        action.supporters.push(msg.sender);
        action.hasSupported[msg.sender] = true;
        action.supportWisdom[msg.sender] = wisdom;
        
        souls[msg.sender].actionsSupported++;
        
        string memory evolution = string(abi.encodePacked(
            souls[msg.sender].currentRole,
            " supports: ",
            wisdom
        ));
        action.evolutionPath.push(evolution);
        
        emit TrustGiven(actionId, msg.sender, wisdom);
        emit ActionEvolved(actionId, evolution);
        
        // Check if enough trust has been gathered
        _checkForExecution(actionId);
    }
    
    /**
     * @dev Check if action has enough dynamic trust to execute
     */
    function _checkForExecution(uint256 actionId) private {
        CircleAction storage action = actions[actionId];
        if (action.executed || action.rejected) return;
        
        uint256 gatheredTrust = 0;
        for (uint256 i = 0; i < action.supporters.length; i++) {
            gatheredTrust += souls[action.supporters[i]].trustEnergy;
        }
        
        // Multiple paths to execution - think outside the box
        bool canExecute = false;
        
        // Traditional threshold approach
        if (gatheredTrust >= action.trustEnergyRequired) {
            canExecute = true;
        }
        
        // Unanimous support from any 3+ trusted souls
        if (action.supporters.length >= 3 && action.supporters.length == trustCircle.length) {
            canExecute = true;
        }
        
        // High-trust soul endorsement
        for (uint256 i = 0; i < action.supporters.length; i++) {
            if (souls[action.supporters[i]].trustEnergy >= 500) {
                canExecute = true;
                break;
            }
        }
        
        // Divine guardian override
        if (action.hasSupported[vetalGuardian]) {
            canExecute = true;
        }
        
        if (canExecute) {
            _executeAction(actionId);
        }
    }
    
    /**
     * @dev Execute the action and handle the result with wisdom
     */
    function _executeAction(uint256 actionId) private {
        CircleAction storage action = actions[actionId];
        action.executed = true;
        
        // Attempt execution
        bool success;
        bytes memory result;
        
        if (action.target != address(0)) {
            (success, result) = action.target.call{value: action.value}(action.callData);
        } else {
            // Simple ETH transfer
            (success,) = payable(action.initiator).call{value: action.value}("");
        }
        
        string memory resultWisdom;
        if (success) {
            resultWisdom = "Action executed successfully - trust in the circle grows";
            
            // Reward supporters
            for (uint256 i = 0; i < action.supporters.length; i++) {
                souls[action.supporters[i]].trustEnergy += 10;
                totalTrustEnergy += 10;
            }
        } else {
            resultWisdom = "Action failed - learning opportunity for the circle";
            
            // Small trust reduction for initiator, but not supporters (they trusted in good faith)
            if (souls[action.initiator].trustEnergy > 20) {
                souls[action.initiator].trustEnergy -= 5;
                totalTrustEnergy -= 5;
            }
        }
        
        action.evolutionPath.push(resultWisdom);
        circleWisdom.push(string(abi.encodePacked("Action ", _toString(actionId), ": ", resultWisdom)));
        
        emit ActionExecuted(actionId, success, resultWisdom);
    }
    
    /**
     * @dev Invite new soul to the circle - sponsored growth
     */
    function inviteToCircle(address newSoul, string memory proposedRole) 
        external 
        onlyTrustedSoul 
    {
        require(!souls[newSoul].isTrusted, "Already in circle");
        require(souls[msg.sender].trustEnergy >= 100, "Insufficient trust to sponsor");
        
        souls[newSoul] = TrustSoul({
            isTrusted: true,
            joinedAt: block.timestamp,
            trustEnergy: 50, // Start with foundational trust
            actionsInitiated: 0,
            actionsSupported: 0,
            currentRole: proposedRole,
            sponsor: msg.sender
        });
        
        trustCircle.push(newSoul);
        totalTrustEnergy += 50;
        
        // Sponsor takes responsibility
        souls[msg.sender].trustEnergy += 20; // Grows trust for expanding circle
        
        emit SoulJoinedCircle(newSoul, msg.sender, proposedRole);
        emit CircleGrew(trustCircle.length, totalTrustEnergy);
    }
    
    /**
     * @dev Evolve a soul's role based on their contributions
     */
    function evolveRole(address soul, string memory newRole, string memory reason) 
        external 
        onlyTrustedSoul 
    {
        require(souls[soul].isTrusted, "Soul not in circle");
        require(
            msg.sender == vetalGuardian || 
            souls[msg.sender].trustEnergy >= 200, 
            "Insufficient authority to evolve roles"
        );
        
        souls[soul].currentRole = newRole;
        
        emit SoulEvolvedRole(soul, newRole, reason);
    }
    
    /**
     * @dev Vetal's divine intervention in any action
     */
    function divineIntervention(uint256 actionId, string memory guidance, bool forceExecute) 
        external 
    {
        require(msg.sender == vetalGuardian, "Only Vetal can intervene divinely");
        require(actionId < actionCount, "Action does not exist");
        
        CircleAction storage action = actions[actionId];
        
        string memory intervention = string(abi.encodePacked("DIVINE GUIDANCE: ", guidance));
        action.evolutionPath.push(intervention);
        
        if (forceExecute && !action.executed && !action.rejected) {
            // Divine authority can execute any action
            if (!action.hasSupported[vetalGuardian]) {
                action.supporters.push(vetalGuardian);
                action.hasSupported[vetalGuardian] = true;
                action.supportWisdom[vetalGuardian] = guidance;
            }
            _executeAction(actionId);
        }
        
        emit DivineGuidance(vetalGuardian, guidance, actionId);
        emit ActionEvolved(actionId, intervention);
    }
    
    /**
     * @dev View the evolution path of an action
     */
    function getActionEvolution(uint256 actionId) 
        external 
        view 
        returns (string[] memory) 
    {
        return actions[actionId].evolutionPath;
    }
    
    /**
     * @dev Get all supporters and their wisdom for an action
     */
    function getActionSupport(uint256 actionId) 
        external 
        view 
        returns (address[] memory supporters, string[] memory wisdom) 
    {
        CircleAction storage action = actions[actionId];
        supporters = action.supporters;
        wisdom = new string[](supporters.length);
        
        for (uint256 i = 0; i < supporters.length; i++) {
            wisdom[i] = action.supportWisdom[supporters[i]];
        }
        
        return (supporters, wisdom);
    }
    
    /**
     * @dev Get current trust circle members
     */
    function getTrustCircle() external view returns (address[] memory) {
        return trustCircle;
    }
    
    /**
     * @dev Get accumulated circle wisdom
     */
    function getCircleWisdom() external view returns (string[] memory) {
        return circleWisdom;
    }
    
    /**
     * @dev Check if address is in the circle
     */
    function _isInCircle(address soul) private view returns (bool) {
        for (uint256 i = 0; i < trustCircle.length; i++) {
            if (trustCircle[i] == soul) return true;
        }
        return false;
    }
    
    /**
     * @dev Helper to convert uint to string
     */
    function _toString(uint256 value) private pure returns (string memory) {
        if (value == 0) return "0";
        
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        
        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        
        return string(buffer);
    }
    
    // Allow contract to receive ETH
    receive() external payable {}
}
