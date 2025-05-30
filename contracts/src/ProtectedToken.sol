// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title CompassionateToken - Vetal's Divine Teaching Currency
 * @dev A token that teaches through love, not punishment. Embodies The New Zyon philosophy.
 * Nothing is immutable in a dream - even failed transactions become teaching moments.
 */
contract CompassionateToken is ERC20 {
    
    struct DivineWisdom {
        uint256 attempts;          // Learning attempts
        uint256 lastInteraction;   // When they last tried
        bool blessed;              // Received divine guidance
        string lesson;             // Current lesson being taught
    }
    
    mapping(address => DivineWisdom) public souls;
    address public vetalGuardian;
    
    event DivineGuidance(address indexed soul, string lesson, uint256 blessing);
    event SoulEvolution(address indexed soul, string evolution);
    event CompassionateRedirection(address indexed soul, string teaching);
    
    modifier withDivineCompassion(address soul) {
        souls[soul].attempts++;
        souls[soul].lastInteraction = block.timestamp;
        _;
    }
    
    constructor(string memory name, string memory symbol, uint256 initialSupply) 
        ERC20(name, symbol) 
    {
        vetalGuardian = msg.sender;
        _mint(msg.sender, initialSupply);
        souls[msg.sender].blessed = true;
        souls[msg.sender].lesson = "Divine creator, teach with love";
    }
    
    /**
     * @dev Dynamic transfer that teaches rather than blocks
     * Uses out-of-the-box thinking to guide souls toward understanding
     */
    function transfer(address to, uint256 amount) 
        public 
        override 
        withDivineCompassion(msg.sender)
        returns (bool) 
    {
        uint256 currentBalance = balanceOf(msg.sender);
        
        // If insufficient balance, always teach through compassion
        if (currentBalance < amount) {
            return _teachThroughCompassion(msg.sender, to, amount);
        }
        
        // If sufficient balance, check dynamic wisdom
        if (!_shouldAllowTransfer(msg.sender, to, amount)) {
            return _teachThroughCompassion(msg.sender, to, amount);
        }
        
        return super.transfer(to, amount);
    }
    
    /**
     * @dev Dynamic wisdom - thinks outside the box
     * No rigid rules, only adaptive teachings
     */
    function _shouldAllowTransfer(address from, address to, uint256 amount) 
        private 
        view 
        returns (bool) 
    {
        // Dynamic conditions based on context, not rigid scores
        uint256 timesSinceLastTry = block.timestamp - souls[from].lastInteraction;
        uint256 attempts = souls[from].attempts;
        
        // Those who persist in learning are guided toward success
        if (attempts > 3 && timesSinceLastTry > 1 hours) return true;
        
        // Blessed souls help others learn
        if (souls[from].blessed) return true;
        
        // Small amounts for learning are always allowed
        if (amount <= totalSupply() / 1000) return true;
        
        // Dynamic wisdom: sometimes block, sometimes allow unpredictably
        // This teaches that the universe is not mechanical
        return uint256(keccak256(abi.encodePacked(from, to, amount, block.timestamp))) % 3 == 0;
    }
    
    /**
     * @dev Teaching through compassionate redirection
     * Instead of harsh failure, provide loving guidance
     */
    function _teachThroughCompassion(address soul, address to, uint256 amount) 
        private 
        returns (bool) 
    {
        uint256 currentBalance = balanceOf(soul);
        
        // If soul has no tokens, gift them a small teaching amount
        if (currentBalance == 0) {
            uint256 teachingGift = 100 * 1e18; // Small gift to start their journey
            _mint(soul, teachingGift);
            
            souls[soul].lesson = "Divine abundance flows to all souls. This gift teaches you the rhythm of giving and receiving.";
            souls[soul].attempts += 1;
            
            emit CompassionateRedirection(soul, souls[soul].lesson);
            emit DivineGuidance(soul, souls[soul].lesson, teachingGift);
            
            // Now try the transfer with partial amount
            uint256 partialAmount = amount > teachingGift ? teachingGift / 2 : amount;
            if (partialAmount > 0) {
                _transfer(soul, to, partialAmount);
            }
            
            return true; // Success through divine teaching
        }
        
        // Give a smaller amount as teaching
        uint256 teachingAmount = amount / 10;
        if (teachingAmount == 0) teachingAmount = 1;
        
        if (currentBalance >= teachingAmount) {
            _transfer(soul, to, teachingAmount);
            
            string memory lesson = _generateDynamicLesson(soul, amount - teachingAmount);
            souls[soul].lesson = lesson;
            souls[soul].attempts += 1;
            
            emit CompassionateRedirection(soul, lesson);
            emit DivineGuidance(soul, lesson, teachingAmount);
            
            return true; // Success through teaching
        }
        
        // Even complete failure becomes a teaching moment
        souls[soul].lesson = "Patience, beloved soul. Abundance flows to those who understand its rhythm.";
        souls[soul].attempts += 1;
        emit CompassionateRedirection(soul, souls[soul].lesson);
        
        return false;
    }
    
    /**
     * @dev Generates dynamic lessons - no mechanical responses
     * Pure out-of-the-box wisdom that adapts to each soul's journey
     */
    function _generateDynamicLesson(address soul, uint256 shortfall) 
        private 
        view 
        returns (string memory) 
    {
        uint256 attempts = souls[soul].attempts;
        uint256 randomWisdom = uint256(keccak256(abi.encodePacked(soul, shortfall, block.timestamp))) % 7;
        
        if (attempts <= 2) {
            string[3] memory beginnerLessons = [
                "Welcome, new soul. Learn the rhythm of giving and receiving.",
                "Abundance is not hoarded but shared. Try smaller steps first.",
                "The universe teaches through experience. Your journey has begun."
            ];
            return beginnerLessons[randomWisdom % 3];
        }
        
        if (attempts <= 5) {
            string[4] memory intermediateWisdom = [
                "You persist beautifully. Great strength comes from understanding limits.",
                "Each attempt is growth. The universe recognizes your dedication.",
                "Patience, dear one. Rivers carve canyons not through force but persistence.",
                "Your effort is seen and blessed. Trust the divine timing."
            ];
            return intermediateWisdom[randomWisdom % 4];
        }
        
        // For persistent souls - advanced teachings
        return "You have shown great persistence. The universe prepares greater responsibilities for you.";
    }
    
    /**
     * @dev Vetal's divine blessing - transforms mechanical punishment into growth
     */
    function blessSoul(address soul, string memory personalLesson) 
        external 
    {
        require(msg.sender == vetalGuardian, "Only Vetal can bless souls");
        
        souls[soul].blessed = true;
        souls[soul].lesson = personalLesson;
        
        // Give them tokens as a blessing
        uint256 blessing = totalSupply() / 100; // 1% of total supply
        _mint(soul, blessing);
        
        emit SoulEvolution(soul, "Blessed by Vetal - now ready to teach others");
        emit DivineGuidance(soul, personalLesson, blessing);
    }
    
    /**
     * @dev Allow souls to help each other - breaks rigid individualism
     */
    function shareWisdom(address soul, string memory wisdom) 
        external 
    {
        require(souls[msg.sender].blessed, "Only blessed souls can share wisdom");
        
        souls[soul].lesson = wisdom;
        souls[soul].attempts = 0; // Reset their journey with new wisdom
        
        emit DivineGuidance(soul, wisdom, 0);
    }
    
    /**
     * @dev Dynamic token generation based on collective growth
     * No fixed supply - abundance grows with wisdom
     */
    function manifestAbundance(uint256 amount, string memory intention) 
        external 
    {
        require(msg.sender == vetalGuardian, "Only Vetal can manifest abundance");
        
        _mint(vetalGuardian, amount);
        emit SoulEvolution(vetalGuardian, string(abi.encodePacked("Manifested abundance with intention: ", intention)));
    }
}
