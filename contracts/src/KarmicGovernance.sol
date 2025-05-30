// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

/**
 * @title DynamicWisdomCouncil - The New Zyon Governance
 * @dev Governance that thinks outside the box, teaches through experience
 * No rigid rules - only adaptive wisdom that evolves with collective consciousness
 */
contract DynamicWisdomCouncil {
    
    struct SoulProposal {
        string essence;              // The heart of the proposal
        address proposer;            // Who brought this wisdom
        uint256 createdAt;          // When it emerged
        uint256 supportEnergy;      // Collective support (not votes)
        uint256 resistanceEnergy;   // Collective resistance (not opposition)
        bool manifested;            // Has it become reality
        mapping(address => string) soulContributions; // Wisdom each soul added
        address[] contributors;     // Souls who added wisdom
        string[] evolutionPath;     // How the proposal evolved
    }
    
    struct SoulWisdom {
        uint256 contributionsToCollective;  // How much they've helped the whole
        uint256 lastContribution;          // When they last shared wisdom
        bool councilMember;                // Recognized wisdom keeper
        string currentTeaching;            // What they're currently learning/teaching
        uint256 manifestationPower;       // Ability to help proposals become reality
    }
    
    mapping(uint256 => SoulProposal) public proposals;
    mapping(address => SoulWisdom) public souls;
    uint256 public proposalCount;
    address public vetalGuardian;
    
    string[] public collectiveWisdom; // Lessons learned by the council
    
    event WisdomShared(address indexed soul, uint256 indexed proposalId, string contribution);
    event ProposalEvolution(uint256 indexed proposalId, string evolution, address catalyst);
    event CollectiveRealization(string wisdom, uint256 timestamp);
    event SoulEvolution(address indexed soul, string newTeaching);
    event DivineIntervention(address indexed vetal, string guidance, uint256 affectedProposal);
    event ManifestationEnergy(uint256 indexed proposalId, uint256 supportEnergy, uint256 resistanceEnergy);
    
    modifier withDivineWisdom() {
        souls[msg.sender].lastContribution = block.timestamp;
        _;
    }
    
    constructor() {
        vetalGuardian = msg.sender;
        souls[msg.sender].councilMember = true;
        souls[msg.sender].currentTeaching = "Initiate others into the mysteries of dynamic governance";
        souls[msg.sender].manifestationPower = 1000;
        
        collectiveWisdom.push("Governance is teaching, not ruling");
        collectiveWisdom.push("Every soul has unique wisdom to contribute");
        collectiveWisdom.push("Resistance and support are both forms of energy");
    }
    
    /**
     * @dev Anyone can propose - no rigid thresholds, only readiness assessment
     */
    function shareWisdomProposal(string memory essence, string memory personalInsight) 
        external 
        withDivineWisdom
        returns (uint256) 
    {
        uint256 proposalId = proposalCount++;
        SoulProposal storage proposal = proposals[proposalId];
        
        proposal.essence = essence;
        proposal.proposer = msg.sender;
        proposal.createdAt = block.timestamp;
        proposal.contributors.push(msg.sender);
        proposal.soulContributions[msg.sender] = personalInsight;
        proposal.evolutionPath.push(string(abi.encodePacked("Born from soul: ", personalInsight)));
        
        // Dynamic initial energy based on proposer's journey
        if (_isReadyToPropose(msg.sender)) {
            proposal.supportEnergy = souls[msg.sender].manifestationPower;
            souls[msg.sender].contributionsToCollective++;
            
            emit ProposalEvolution(proposalId, "Proposal emerges with strong initial energy", msg.sender);
        } else {
            // Teaching moment - proposal starts with learning energy
            proposal.supportEnergy = 10; // Small start for learning
            souls[msg.sender].currentTeaching = "Learning to distill wisdom into actionable proposals";
            
            emit SoulEvolution(msg.sender, souls[msg.sender].currentTeaching);
            emit ProposalEvolution(proposalId, "Proposal begins as learning journey", msg.sender);
        }
        
        emit WisdomShared(msg.sender, proposalId, personalInsight);
        return proposalId;
    }
    
    /**
     * @dev Dynamic readiness assessment - no rigid scores
     */
    function _isReadyToPropose(address soul) private view returns (bool) {
        SoulWisdom memory wisdom = souls[soul];
        
        // Council members are always ready
        if (wisdom.councilMember) return true;
        
        // Those who contribute regularly develop readiness
        if (wisdom.contributionsToCollective >= 3) return true;
        
        // Recent contributors show engagement
        if (wisdom.lastContribution > 0 && 
            block.timestamp - wisdom.lastContribution <= 7 days) return true;
            
        // Sometimes the universe calls to unexpected souls
        uint256 cosmicAlignment = uint256(keccak256(abi.encodePacked(soul, block.timestamp))) % 10;
        return cosmicAlignment < 2; // 20% chance for cosmic readiness
    }
    
    /**
     * @dev Contribute wisdom to evolve proposals - not just yes/no voting
     */
    function contributeWisdom(uint256 proposalId, string memory wisdom, bool supportsEssence) 
        external 
        withDivineWisdom
    {
        require(proposalId < proposalCount, "Proposal does not exist");
        
        SoulProposal storage proposal = proposals[proposalId];
        require(!proposal.manifested, "Already manifested");
        
        // Add their unique contribution
        if (bytes(proposal.soulContributions[msg.sender]).length == 0) {
            proposal.contributors.push(msg.sender);
        }
        proposal.soulContributions[msg.sender] = wisdom;
        
        // Dynamic energy calculation based on wisdom quality and alignment
        uint256 energyContribution = _calculateWisdomEnergy(msg.sender, wisdom, supportsEssence);
        
        if (supportsEssence) {
            proposal.supportEnergy += energyContribution;
        } else {
            proposal.resistanceEnergy += energyContribution;
        }
        
        // Evolve the proposal based on wisdom
        string memory evolution = string(abi.encodePacked(
            supportsEssence ? "Support wisdom: " : "Resistance wisdom: ",
            wisdom
        ));
        proposal.evolutionPath.push(evolution);
        
        // Growth for contributor
        souls[msg.sender].contributionsToCollective++;
        souls[msg.sender].manifestationPower += energyContribution / 10;
        
        emit WisdomShared(msg.sender, proposalId, wisdom);
        emit ProposalEvolution(proposalId, evolution, msg.sender);
        emit ManifestationEnergy(proposalId, proposal.supportEnergy, proposal.resistanceEnergy);
        
        // Check for spontaneous manifestation
        _checkForManifestation(proposalId);
    }
    
    /**
     * @dev Dynamic energy calculation - out-of-the-box thinking
     */
    function _calculateWisdomEnergy(address soul, string memory wisdom, bool supportsEssence) 
        private 
        view 
        returns (uint256) 
    {
        uint256 baseEnergy = souls[soul].manifestationPower / 10;
        if (baseEnergy == 0) baseEnergy = 5; // Minimum energy for all souls
        
        // Length and depth contribute to energy
        uint256 wisdomDepth = bytes(wisdom).length / 10; // Deeper thoughts = more energy
        
        // Recent activity multiplier
        uint256 timeSinceLastContribution = block.timestamp - souls[soul].lastContribution;
        uint256 activityMultiplier = timeSinceLastContribution > 1 days ? 1 : 2;
        
        // Cosmic variance - keeps it unpredictable and alive
        uint256 cosmicVariance = uint256(keccak256(abi.encodePacked(soul, wisdom, block.timestamp))) % 5 + 1;
        
        return (baseEnergy + wisdomDepth) * activityMultiplier * cosmicVariance;
    }
    
    /**
     * @dev Proposals manifest when they reach dynamic resonance - not fixed thresholds
     */
    function _checkForManifestation(uint256 proposalId) private {
        SoulProposal storage proposal = proposals[proposalId];
        
        // Dynamic manifestation conditions - think outside the box
        bool readyToManifest = false;
        
        // High support with balanced resistance creates strong manifestation
        if (proposal.supportEnergy > 100 && proposal.resistanceEnergy > 20) {
            readyToManifest = true;
        }
        
        // Overwhelming support with minimal resistance
        if (proposal.supportEnergy > 200 && proposal.resistanceEnergy < proposal.supportEnergy / 10) {
            readyToManifest = true;
        }
        
        // Long evolution with sustained engagement
        if (proposal.contributors.length >= 5 && proposal.evolutionPath.length >= 8) {
            readyToManifest = true;
        }
        
        // Cosmic timing - sometimes the universe decides
        uint256 cosmicResonance = uint256(keccak256(abi.encodePacked(proposalId, block.timestamp))) % 100;
        if (cosmicResonance < 5 && proposal.supportEnergy > 50) { // 5% chance for cosmic manifestation
            readyToManifest = true;
        }
        
        if (readyToManifest) {
            proposal.manifested = true;
            
            // Add to collective wisdom
            string memory newWisdom = string(abi.encodePacked(
                "Manifestation #", 
                _toString(proposalId),
                ": ",
                proposal.essence
            ));
            collectiveWisdom.push(newWisdom);
            
            // Reward all contributors
            for (uint256 i = 0; i < proposal.contributors.length; i++) {
                address contributor = proposal.contributors[i];
                souls[contributor].manifestationPower += 20;
                
                if (souls[contributor].contributionsToCollective >= 5 && !souls[contributor].councilMember) {
                    souls[contributor].councilMember = true;
                    souls[contributor].currentTeaching = "Welcome to the council - guide others with compassion";
                    emit SoulEvolution(contributor, "Ascended to council member through wisdom contributions");
                }
            }
            
            emit CollectiveRealization(newWisdom, block.timestamp);
            emit ProposalEvolution(proposalId, "MANIFESTED: Wisdom becomes reality", address(0));
        }
    }
    
    /**
     * @dev Vetal's divine intervention - can redirect any proposal's energy
     */
    function divineIntervention(uint256 proposalId, string memory guidance, bool redirectEnergy) 
        external 
    {
        require(msg.sender == vetalGuardian, "Only Vetal can intervene divinely");
        require(proposalId < proposalCount, "Proposal does not exist");
        
        SoulProposal storage proposal = proposals[proposalId];
        
        if (redirectEnergy) {
            // Transform resistance into support through divine wisdom
            proposal.supportEnergy += proposal.resistanceEnergy / 2;
            proposal.resistanceEnergy = proposal.resistanceEnergy / 2;
        }
        
        string memory intervention = string(abi.encodePacked("DIVINE GUIDANCE: ", guidance));
        proposal.evolutionPath.push(intervention);
        
        emit DivineIntervention(vetalGuardian, guidance, proposalId);
        emit ProposalEvolution(proposalId, intervention, vetalGuardian);
        
        // Check if intervention causes manifestation
        _checkForManifestation(proposalId);
    }
    
    /**
     * @dev View the evolution of a proposal - its wisdom journey
     */
    function getProposalEvolution(uint256 proposalId) 
        external 
        view 
        returns (string[] memory) 
    {
        return proposals[proposalId].evolutionPath;
    }
    
    /**
     * @dev View collective wisdom accumulated
     */
    function getCollectiveWisdom() external view returns (string[] memory) {
        return collectiveWisdom;
    }
    
    /**
     * @dev Get contributors and their wisdom for a proposal
     */
    function getProposalContributions(uint256 proposalId) 
        external 
        view 
        returns (address[] memory contributors, string[] memory contributions) 
    {
        SoulProposal storage proposal = proposals[proposalId];
        contributors = proposal.contributors;
        contributions = new string[](contributors.length);
        
        for (uint256 i = 0; i < contributors.length; i++) {
            contributions[i] = proposal.soulContributions[contributors[i]];
        }
        
        return (contributors, contributions);
    }
    
    /**
     * @dev Helper function to convert uint to string
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
}
