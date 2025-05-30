// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

/**
 * @title LivingAbundanceDistributor - Vetal's Divine Treasury
 * @dev A vault that breathes, learns, and grows abundance organically
 * No rigid rules - only dynamic wisdom that teaches through abundance and scarcity
 */
contract LivingAbundanceDistributor {
    
    struct SoulAccount {
        uint256 contribution;        // What they've added to collective abundance
        uint256 withdrawn;           // What they've taken from collective abundance
        uint256 lastInteraction;     // When they last engaged
        uint256 abundanceScore;      // Dynamic measure of their abundance consciousness
        bool abundancePartner;       // Can they participate in abundance flows
        string currentLesson;        // What the vault is teaching them
        uint256 teachingMoments;     // How many times vault has guided them
        address mentor;              // Who introduced them to abundance consciousness
    }
    
    struct AbundanceFlow {
        address requester;           // Who requested abundance
        uint256 amount;             // How much abundance requested
        string intention;           // Why they need abundance
        uint256 createdAt;          // When the request was made
        mapping(address => bool) hasSupported; // Who supports this flow
        mapping(address => string) supportReason; // Why they support
        address[] supporters;       // List of supporters
        bool fulfilled;             // Has abundance flowed
        bool redirected;            // Was it redirected to teaching
        uint256 actualAmount;       // What actually flowed (may be different)
        string[] wisdomPath;        // How the request evolved
    }
    
    mapping(address => SoulAccount) public souls;
    mapping(uint256 => AbundanceFlow) public flows;
    uint256 public flowCount;
    address public vetalGuardian;
    
    uint256 public totalAbundance;           // Current vault balance
    uint256 public totalContributions;      // All time contributions
    uint256 public totalTeachingMoments;    // How many lessons given
    string[] public abundanceWisdom;        // Wisdom learned by the vault
    
    event AbundanceReceived(address indexed soul, uint256 amount, uint256 newAbundanceScore);
    event AbundanceRequested(uint256 indexed flowId, address indexed soul, uint256 amount, string intention);
    event FlowSupported(uint256 indexed flowId, address indexed supporter, string reason);
    event AbundanceFulfilled(uint256 indexed flowId, uint256 actualAmount, string wisdom);
    event TeachingMoment(address indexed soul, string lesson, uint256 redirectedAmount);
    event AbundanceEvolution(address indexed soul, string evolution, uint256 newScore);
    event VaultWisdom(string wisdom, uint256 timestamp);
    event DivineAbundance(address indexed vetal, uint256 amount, string manifestation);
    
    modifier withAbundanceWisdom() {
        souls[msg.sender].lastInteraction = block.timestamp;
        _;
    }
    
    constructor() {
        vetalGuardian = msg.sender;
        souls[msg.sender].abundancePartner = true;
        souls[msg.sender].abundanceScore = 1000;
        souls[msg.sender].currentLesson = "Divine abundance flows through teaching and compassion";
        
        abundanceWisdom.push("Abundance is not hoarded but shared");
        abundanceWisdom.push("Every interaction with abundance is a teaching moment");
        abundanceWisdom.push("Scarcity consciousness creates scarcity; abundance consciousness creates abundance");
        abundanceWisdom.push("The vault learns and evolves with every soul it serves");
    }
    
    /**
     * @dev Contribute to collective abundance - always accepted with teaching
     */
    function contributeAbundance(string memory intention) 
        external 
        payable 
        withAbundanceWisdom 
    {
        require(msg.value > 0, "Cannot contribute emptiness");
        
        souls[msg.sender].contribution += msg.value;
        totalAbundance += msg.value;
        totalContributions += msg.value;
        
        // Dynamic abundance score growth
        uint256 scoreIncrease = _calculateAbundanceGrowth(msg.sender, msg.value);
        souls[msg.sender].abundanceScore += scoreIncrease;
        
        // First-time contributors become abundance partners
        if (!souls[msg.sender].abundancePartner) {
            souls[msg.sender].abundancePartner = true;
            souls[msg.sender].currentLesson = "Welcome to abundance consciousness - learn to flow resources wisely";
            
            emit AbundanceEvolution(msg.sender, "Became abundance partner through contribution", souls[msg.sender].abundanceScore);
        }
        
        // Large contributions receive special recognition
        if (msg.value >= 1 ether) {
            souls[msg.sender].abundanceScore += 100;
            abundanceWisdom.push(string(abi.encodePacked("Large abundance contribution: ", intention)));
            emit VaultWisdom(string(abi.encodePacked("Generous soul shared: ", intention)), block.timestamp);
        }
        
        emit AbundanceReceived(msg.sender, msg.value, souls[msg.sender].abundanceScore);
    }
    
    /**
     * @dev Dynamic abundance score calculation - out-of-the-box thinking
     */
    function _calculateAbundanceGrowth(address soul, uint256 contribution) 
        private 
        view 
        returns (uint256) 
    {
        uint256 baseGrowth = contribution / 1e16; // Base: 1 score per 0.01 ETH
        
        // First-time contributors get bonus
        if (souls[soul].contribution == 0) baseGrowth += 50;
        
        // Frequent contributors get compounding bonus
        uint256 timeSinceLastInteraction = block.timestamp - souls[soul].lastInteraction;
        if (timeSinceLastInteraction <= 1 days) baseGrowth = (baseGrowth * 150) / 100; // 50% bonus
        
        // Those who've been taught well and come back grow faster
        if (souls[soul].teachingMoments >= 3) baseGrowth = (baseGrowth * 120) / 100; // 20% bonus
        
        // Cosmic variance keeps it alive and unpredictable
        uint256 cosmicBonus = uint256(keccak256(abi.encodePacked(soul, contribution, block.timestamp))) % 20;
        
        return baseGrowth + cosmicBonus;
    }
    
    /**
     * @dev Request abundance flow - not withdrawal, but conscious request
     */
    function requestAbundanceFlow(uint256 amount, string memory intention) 
        external 
        withAbundanceWisdom 
        returns (uint256) 
    {
        require(amount > 0, "Cannot request emptiness");
        require(bytes(intention).length > 10, "Intention must be clear and heartfelt");
        
        uint256 flowId = flowCount++;
        AbundanceFlow storage flow = flows[flowId];
        
        flow.requester = msg.sender;
        flow.amount = amount;
        flow.intention = intention;
        flow.createdAt = block.timestamp;
        flow.wisdomPath.push(string(abi.encodePacked("Requested by soul: ", intention)));
        
        // Check if they can get immediate abundance or need teaching
        if (_canReceiveImmediateAbundance(msg.sender, amount)) {
            _fulfillAbundanceFlow(flowId, amount, "Immediate abundance - soul demonstrates readiness");
        } else {
            souls[msg.sender].currentLesson = _generateAbundanceTeaching(msg.sender, amount);
            souls[msg.sender].teachingMoments++;
            totalTeachingMoments++;
            
            emit TeachingMoment(msg.sender, souls[msg.sender].currentLesson, 0);
        }
        
        emit AbundanceRequested(flowId, msg.sender, amount, intention);
        return flowId;
    }
    
    /**
     * @dev Dynamic abundance readiness assessment
     */
    function _canReceiveImmediateAbundance(address soul, uint256 amount) 
        private 
        view 
        returns (bool) 
    {
        SoulAccount memory account = souls[soul];
        
        // Abundance partners who've contributed can flow
        if (account.abundancePartner && account.contribution > 0) {
            
            // Can't take more than 2x what they've contributed (unless high abundance score)
            if (amount <= account.contribution * 2 || account.abundanceScore >= 500) {
                return true;
            }
            
            // Small amounts for learning always flow
            if (amount <= 0.01 ether) return true;
        }
        
        // High abundance consciousness souls get abundance
        if (account.abundanceScore >= 300) return true;
        
        // Those learning well get increasing access
        if (account.teachingMoments >= 5 && amount <= 0.1 ether) return true;
        
        // Sometimes the universe gives unexpected gifts
        uint256 cosmicGift = uint256(keccak256(abi.encodePacked(soul, amount, block.timestamp))) % 20;
        return cosmicGift == 0; // 5% chance for cosmic gift
    }
    
    /**
     * @dev Generate dynamic abundance teaching
     */
    function _generateAbundanceTeaching(address soul, uint256 requestedAmount) 
        private 
        view 
        returns (string memory) 
    {
        SoulAccount memory account = souls[soul];
        uint256 teachingVariant = uint256(keccak256(abi.encodePacked(soul, requestedAmount, block.timestamp))) % 6;
        
        if (!account.abundancePartner) {
            return "To receive abundance, first learn to give abundance. Contribute to the collective flow.";
        }
        
        if (account.contribution == 0) {
            return "Abundance flows to those who first understand its source. Share what you have, then ask for more.";
        }
        
        if (requestedAmount > account.contribution * 3) {
            return "Great abundance requires great consciousness. Build your abundance score through mindful actions.";
        }
        
        string[6] memory wisdomTeachings = [
            "Abundance is not taken but received. Show the universe your readiness through patience.",
            "Every request is a conversation with the cosmos. What are you truly asking for?",
            "Large abundance flows to those who've proven they can handle small abundance wisely.",
            "The vault sees your heart's intention. Purify your request and try again.",
            "Abundance consciousness grows through giving, not just receiving. Share your gifts first.",
            "Trust the divine timing. What you need will flow when you're truly ready."
        ];
        
        return wisdomTeachings[teachingVariant];
    }
    
    /**
     * @dev Support someone else's abundance flow - creates community
     */
    function supportAbundanceFlow(uint256 flowId, string memory reason) 
        external 
        withAbundanceWisdom 
    {
        require(flowId < flowCount, "Flow does not exist");
        require(souls[msg.sender].abundancePartner, "Must be abundance partner to support flows");
        
        AbundanceFlow storage flow = flows[flowId];
        require(!flow.fulfilled && !flow.redirected, "Flow already completed");
        require(!flow.hasSupported[msg.sender], "Already supported this flow");
        require(flow.requester != msg.sender, "Cannot support your own flow");
        
        flow.supporters.push(msg.sender);
        flow.hasSupported[msg.sender] = true;
        flow.supportReason[msg.sender] = reason;
        
        string memory supportWisdom = string(abi.encodePacked("Supported by community: ", reason));
        flow.wisdomPath.push(supportWisdom);
        
        // Supporter gains abundance score for helping others
        souls[msg.sender].abundanceScore += 10;
        
        emit FlowSupported(flowId, msg.sender, reason);
        
        // Check if enough community support has gathered
        _checkForCommunityAbundance(flowId);
    }
    
    /**
     * @dev Check if community support enables abundance flow
     */
    function _checkForCommunityAbundance(uint256 flowId) private {
        AbundanceFlow storage flow = flows[flowId];
        
        // Community support can enable flows that individual readiness couldn't
        if (flow.supporters.length >= 3) {
            // Calculate collective abundance score of supporters
            uint256 collectiveScore = 0;
            for (uint256 i = 0; i < flow.supporters.length; i++) {
                collectiveScore += souls[flow.supporters[i]].abundanceScore;
            }
            
            // Strong community support can fulfill the flow
            if (collectiveScore >= 300) {
                uint256 actualAmount = flow.amount;
                
                // Large requests get partial fulfillment to teach gradual growth
                if (flow.amount > 1 ether) {
                    actualAmount = flow.amount / 2;
                }
                
                _fulfillAbundanceFlow(flowId, actualAmount, "Community abundance - supported by collective wisdom");
                
                // Reward supporters
                for (uint256 i = 0; i < flow.supporters.length; i++) {
                    souls[flow.supporters[i]].abundanceScore += 20;
                }
            }
        }
    }
    
    /**
     * @dev Fulfill abundance flow with teaching
     */
    function _fulfillAbundanceFlow(uint256 flowId, uint256 actualAmount, string memory wisdom) 
        private 
    {
        AbundanceFlow storage flow = flows[flowId];
        require(actualAmount <= totalAbundance, "Insufficient vault abundance");
        
        flow.fulfilled = true;
        flow.actualAmount = actualAmount;
        flow.wisdomPath.push(wisdom);
        
        // Update soul's account
        souls[flow.requester].withdrawn += actualAmount;
        totalAbundance -= actualAmount;
        
        // Growth for receiving abundance mindfully
        souls[flow.requester].abundanceScore += actualAmount / 1e16; // Score grows with abundance received
        
        // Transfer the abundance
        (bool success,) = payable(flow.requester).call{value: actualAmount}("");
        require(success, "Abundance transfer failed");
        
        // Add to vault wisdom
        abundanceWisdom.push(string(abi.encodePacked("Flow ", _toString(flowId), ": ", wisdom)));
        
        emit AbundanceFulfilled(flowId, actualAmount, wisdom);
        
        // If they received less than requested, teach them why
        if (actualAmount < flow.amount) {
            string memory partialLesson = "Partial abundance teaches gradual growth. Demonstrate wisdom with this, and more will flow.";
            souls[flow.requester].currentLesson = partialLesson;
            souls[flow.requester].teachingMoments++;
            
            emit TeachingMoment(flow.requester, partialLesson, flow.amount - actualAmount);
        }
    }
    
    /**
     * @dev Invite someone to abundance consciousness
     */
    function inviteToAbundance(address soul, string memory welcomeMessage) 
        external 
    {
        require(souls[msg.sender].abundancePartner, "Must be abundance partner to invite others");
        require(!souls[soul].abundancePartner, "Already an abundance partner");
        require(souls[msg.sender].abundanceScore >= 200, "Need higher abundance consciousness to invite others");
        
        souls[soul].abundancePartner = true;
        souls[soul].abundanceScore = 50; // Starting bonus
        souls[soul].currentLesson = welcomeMessage;
        souls[soul].mentor = msg.sender;
        
        // Mentor gains abundance score for growing the community
        souls[msg.sender].abundanceScore += 30;
        
        emit AbundanceEvolution(soul, string(abi.encodePacked("Invited by mentor: ", welcomeMessage)), 50);
    }
    
    /**
     * @dev Vetal's divine abundance manifestation
     */
    function manifestDivineAbundance(uint256 amount, string memory manifestation) 
        external 
        payable 
    {
        require(msg.sender == vetalGuardian, "Only Vetal can manifest divine abundance");
        
        uint256 totalManifested = msg.value + amount;
        totalAbundance += totalManifested;
        souls[vetalGuardian].contribution += totalManifested;
        
        abundanceWisdom.push(string(abi.encodePacked("Divine manifestation: ", manifestation)));
        
        emit DivineAbundance(vetalGuardian, totalManifested, manifestation);
        emit VaultWisdom(manifestation, block.timestamp);
    }
    
    /**
     * @dev Vetal's intervention in any abundance flow
     */
    function divineAbundanceIntervention(uint256 flowId, uint256 overrideAmount, string memory guidance) 
        external 
    {
        require(msg.sender == vetalGuardian, "Only Vetal can intervene divinely");
        require(flowId < flowCount, "Flow does not exist");
        
        AbundanceFlow storage flow = flows[flowId];
        require(!flow.fulfilled && !flow.redirected, "Flow already completed");
        
        if (overrideAmount > 0 && overrideAmount <= totalAbundance) {
            _fulfillAbundanceFlow(flowId, overrideAmount, string(abi.encodePacked("DIVINE INTERVENTION: ", guidance)));
        } else {
            flow.redirected = true;
            souls[flow.requester].currentLesson = guidance;
            souls[flow.requester].teachingMoments++;
            
            emit TeachingMoment(flow.requester, guidance, flow.amount);
        }
    }
    
    /**
     * @dev View flow evolution path
     */
    function getFlowWisdom(uint256 flowId) 
        external 
        view 
        returns (string[] memory) 
    {
        return flows[flowId].wisdomPath;
    }
    
    /**
     * @dev Get flow supporters and their reasons
     */
    function getFlowSupport(uint256 flowId) 
        external 
        view 
        returns (address[] memory supporters, string[] memory reasons) 
    {
        AbundanceFlow storage flow = flows[flowId];
        supporters = flow.supporters;
        reasons = new string[](supporters.length);
        
        for (uint256 i = 0; i < supporters.length; i++) {
            reasons[i] = flow.supportReason[supporters[i]];
        }
        
        return (supporters, reasons);
    }
    
    /**
     * @dev Get vault's accumulated wisdom
     */
    function getAbundanceWisdom() external view returns (string[] memory) {
        return abundanceWisdom;
    }
    
    /**
     * @dev Get vault statistics
     */
    function getVaultStats() 
        external 
        view 
        returns (
            uint256 balance,
            uint256 totalContributed,
            uint256 totalLessons,
            uint256 wisdomCount
        ) 
    {
        return (
            totalAbundance,
            totalContributions,
            totalTeachingMoments,
            abundanceWisdom.length
        );
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
    
    // Allow contract to receive ETH directly
    receive() external payable {
        totalAbundance += msg.value;
        souls[msg.sender].contribution += msg.value;
        
        emit AbundanceReceived(msg.sender, msg.value, souls[msg.sender].abundanceScore);
    }
}
