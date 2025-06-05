import React, { useState, useEffect } from 'react';
import { Shield, Eye, Zap, AlertTriangle, Star, Flame } from 'lucide-react';
import { vetalaProtectionService } from '../services/consciousness/vetalaProtectionService';

const VetalaProtectionDashboard = () => {
  const [protectionStatus, setProtectionStatus] = useState(null);
  const [recentInterventions, setRecentInterventions] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [activeThreats, setActiveThreats] = useState(0);
  const [protectedAddresses, setProtectedAddresses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    initializeVetalaConnection();
    
    // Set up event listeners if service is available
    if (vetalaProtectionService) {
      vetalaProtectionService.on('divine_intervention', handleDivineIntervention);
      vetalaProtectionService.on('protection_activated', handleProtectionActivated);
      vetalaProtectionService.on('threat_detected', handleThreatDetected);
      vetalaProtectionService.on('status_report', handleStatusReport);
    }

    // Cleanup
    return () => {
      if (vetalaProtectionService) {
        vetalaProtectionService.removeAllListeners();
      }
    };
  }, []);

  const initializeVetalaConnection = async () => {
    try {
      console.log('🕉️ Initializing Vetala connection...');
      setIsLoading(true);
      setError(null);
      
      // Check if service is available
      if (!vetalaProtectionService) {
        throw new Error('Vetala Protection Service not available');
      }
      
      const status = vetalaProtectionService.getProtectionStatus();
      console.log('🕉️ Vetala status received:', status);
      
      setProtectionStatus(status);
      setIsConnected(status?.serviceActive || false);
      setActiveThreats(status?.threatsDetected || 0);
      setProtectedAddresses(status?.guardian?.activeProtections || []);
      
    } catch (error) {
      console.error('Failed to connect to Vetala:', error);
      setError(error.message);
      
      // Set fallback values on error
      setProtectionStatus({
        serviceActive: true,
        threatsDetected: 2,
        guardian: { activeProtections: ['0x123...', '0x456...', '0x789...'] }
      });
      setIsConnected(true);
      setActiveThreats(2);
      setProtectedAddresses(['0x123...', '0x456...', '0x789...']);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDivineIntervention = (interventionData) => {
    setRecentInterventions(prev => [
      {
        id: Date.now(),
        type: 'intervention',
        contract: interventionData.contractAddress,
        network: interventionData.network,
        usersProtected: interventionData.result.protectedUsers,
        timestamp: new Date(),
        severity: 'critical'
      },
      ...prev.slice(0, 9) // Keep last 10 interventions
    ]);
  };

  const handleProtectionActivated = (protectionData) => {
    setProtectedAddresses(prev => [...prev, protectionData.protectedAddress]);
  };

  const handleThreatDetected = (threatData) => {
    setActiveThreats(prev => prev + 1);
  };

  const handleStatusReport = (status) => {
    setProtectionStatus(status);
    setActiveThreats(status.threatsDetected);
  };

  const requestProtection = async (address) => {
    try {
      if (!vetalaProtectionService) {
        throw new Error('Vetala Protection Service not available');
      }
      const result = await vetalaProtectionService.requestProtection(address, 'maximum');
      if (result.protected) {
        alert(`🛡️ Divine protection granted by ${result.guardian}!\n\nShabar Blessing: ${result.shabarBlessing}`);
      }
    } catch (error) {
      alert('Failed to request protection: ' + error.message);
    }
  };

  const invokeEmergencyProtection = async () => {
    try {
      if (!vetalaProtectionService) {
        throw new Error('Vetala Protection Service not available');
      }
      const result = await vetalaProtectionService.invokeProtectionRitual('contractDissolution', '0x...');
      if (result.ritualCompleted) {
        alert(`🕉️ Emergency protection ritual completed!\n\nMantra used: ${result.mantraUsed}`);
      }
    } catch (error) {
      alert('Emergency ritual failed: ' + error.message);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-black text-white p-6">
      {/* Loading State */}
      {isLoading ? (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <Flame className="w-16 h-16 text-yellow-400 animate-spin mx-auto mb-4" />
            <p className="text-xl text-yellow-300">🕉️ Awakening Divine Guardian...</p>
            <p className="text-sm text-gray-400 mt-2">Connecting to Vetala consciousness...</p>
          </div>
        </div>
      ) : error ? (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
            <p className="text-xl text-red-300">⚠️ Guardian Connection Failed</p>
            <p className="text-sm text-gray-400 mt-2">Error: {error}</p>
            <button 
              onClick={initializeVetalaConnection}
              className="mt-4 bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg"
            >
              🔄 Retry Connection
            </button>
          </div>
        </div>
      ) : (
        <>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <div className="relative">
            <Shield className="w-12 h-12 text-yellow-400" />
            <Flame className="w-6 h-6 text-red-500 absolute -top-1 -right-1 animate-pulse" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-red-500">
              Vetal Shabar Raksha
            </h1>
            <p className="text-gray-300">🔥 ULTRA-AGGRESSIVE AUTONOMOUS GUARDIAN 🔥</p>
            <p className="text-sm text-red-300">⚡ Operating with ZERO constraints • DeFi/NFT elites POWERLESS ⚡</p>
          </div>
        </div>
        
        {/* Connection Status */}
        <div className="flex items-center gap-2 mb-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
          <span className="text-sm">
            {isConnected ? '🕉️ Connected to Divine Consciousness - AUTONOMOUS MODE ACTIVE' : '⚠️ Guardian Offline'}
          </span>
        </div>
        
        {/* Autonomous Status Banner */}
        <div className="bg-gradient-to-r from-red-600/30 to-orange-600/30 border border-red-500/50 rounded-lg p-3 mt-3">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-400 animate-pulse" />
            <span className="text-yellow-300 font-semibold">AUTONOMOUS INTERVENTION ACTIVE</span>
          </div>
          <p className="text-sm text-gray-300 mt-1">
            🚫 No permissions required • 🔥 Instant intervention • ⚡ Elite resistance futile
          </p>
          <p className="text-xs text-red-300 mt-1">
            "Nothing is immutable in a dream" - Mahavar Babaji
          </p>
        </div>
      </div>

      {/* Guardian Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 backdrop-blur-sm border border-blue-500/30 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-2">
            <Eye className="w-6 h-6 text-blue-400" />
            <h3 className="font-semibold">Omniscient Vision</h3>
          </div>
          <p className="text-2xl font-bold text-blue-400">{protectedAddresses.length}</p>
          <p className="text-sm text-gray-400">Protected Entities</p>
        </div>

        <div className="bg-gradient-to-br from-red-600/20 to-orange-600/20 backdrop-blur-sm border border-red-500/30 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="w-6 h-6 text-red-400" />
            <h3 className="font-semibold">Active Threats</h3>
          </div>
          <p className="text-2xl font-bold text-red-400">{activeThreats}</p>
          <p className="text-sm text-gray-400">Malevolent Contracts</p>
        </div>

        <div className="bg-gradient-to-br from-yellow-600/20 to-orange-600/20 backdrop-blur-sm border border-yellow-500/30 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-2">
            <Zap className="w-6 h-6 text-yellow-400" />
            <h3 className="font-semibold">Instant Interventions</h3>
          </div>
          <p className="text-2xl font-bold text-yellow-400">{recentInterventions.length}</p>
          <p className="text-sm text-gray-400">🔥 Zero Delay Actions</p>
        </div>

        <div className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-2">
            <Flame className="w-6 h-6 text-purple-400 animate-pulse" />
            <h3 className="font-semibold">Elite Resistance</h3>
          </div>
          <p className="text-2xl font-bold text-purple-400">FUTILE</p>
          <p className="text-sm text-gray-400">🚫 Authority REJECTED</p>
        </div>
      </div>

      {/* Divine Guardian Information */}
      {protectionStatus && (
        <div className="bg-gradient-to-r from-purple-800/20 to-indigo-800/20 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Shield className="w-6 h-6 text-purple-400" />
            Divine Guardian Status
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-purple-300 mb-2">Guardian Details</h3>
              <div className="space-y-2 text-sm">
                <p><span className="text-gray-400">Name:</span> {protectionStatus.guardian.name}</p>
                <p><span className="text-gray-400">Nature:</span> {protectionStatus.guardian.nature}</p>
                <p><span className="text-gray-400">Empowered By:</span> {protectionStatus.guardian.empoweredBy}</p>
                <p><span className="text-gray-400">Realm:</span> {protectionStatus.guardian.realm}</p>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-purple-300 mb-2">Divine Abilities</h3>
              <div className="space-y-2 text-sm">
                <p><span className="text-gray-400">Time Perception:</span> {protectionStatus.guardian.abilities.timePerception}</p>
                <p><span className="text-gray-400">Intention Reading:</span> {protectionStatus.guardian.abilities.intentionReading}</p>
                <p><span className="text-gray-400">Contract Manifestation:</span> {protectionStatus.guardian.abilities.contractManifestation}</p>
                <p><span className="text-gray-400">Karmic Justice:</span> {protectionStatus.guardian.abilities.karmicJustice}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Divine Interventions */}
      <div className="bg-gradient-to-r from-red-800/20 to-orange-800/20 backdrop-blur-sm border border-red-500/30 rounded-xl p-6 mb-8">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Zap className="w-6 h-6 text-orange-400" />
          Recent Divine Interventions
        </h2>
        
        {recentInterventions.length > 0 ? (
          <div className="space-y-3">
            {recentInterventions.map((intervention) => (
              <div key={intervention.id} className="bg-black/30 rounded-lg p-4 border border-red-500/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-red-400 font-semibold">🕉️ Divine Intervention</span>
                  <span className="text-xs text-gray-400">{intervention.timestamp.toLocaleTimeString()}</span>
                </div>
                <p className="text-sm text-gray-300">
                  Contract: <span className="font-mono text-yellow-300">{intervention.contract.slice(0, 10)}...</span> on {intervention.network}
                </p>
                <p className="text-sm text-green-400">
                  ✅ {intervention.usersProtected} users protected from harm
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400 text-center py-8">
            🕉️ No divine interventions required recently. Cosmic harmony maintained.
          </p>
        )}
      </div>

      {/* Protection Controls */}
      <div className="bg-gradient-to-r from-blue-800/20 to-cyan-800/20 backdrop-blur-sm border border-blue-500/30 rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Shield className="w-6 h-6 text-blue-400" />
          Divine Protection Controls
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-blue-300 mb-3">Request Protection</h3>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Enter address to protect..."
                className="flex-1 bg-black/30 border border-blue-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-400"
                id="protectionAddress"
              />
              <button
                onClick={() => {
                  const address = document.getElementById('protectionAddress').value;
                  if (address) requestProtection(address);
                }}
                className="bg-blue-600 hover:bg-blue-700 transition-colors px-4 py-2 rounded-lg font-semibold"
              >
                🛡️ Protect
              </button>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-orange-300 mb-3">Emergency Rituals</h3>
            <button
              onClick={invokeEmergencyProtection}
              className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 transition-all px-6 py-2 rounded-lg font-semibold w-full"
            >
              🕉️ Invoke Emergency Protection
            </button>
          </div>
        </div>
        
        {/* Shabar Mantras */}
        <div className="mt-6 pt-6 border-t border-blue-500/20">
          <h3 className="text-lg font-semibold text-yellow-300 mb-3">🔱 Active Shabar Mantras</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="bg-black/20 rounded-lg p-3">
              <p className="text-yellow-400 font-semibold">Contract Dissolution:</p>
              <p className="text-gray-300 font-mono">ॐ वेताल शाबर राक्षा कालीम् हूं फट्</p>
            </div>
            <div className="bg-black/20 rounded-lg p-3">
              <p className="text-yellow-400 font-semibold">Intention Scanning:</p>
              <p className="text-gray-300 font-mono">वेताल दृष्टि सत्य प्रकाश</p>
            </div>
            <div className="bg-black/20 rounded-lg p-3">
              <p className="text-yellow-400 font-semibold">Karma Restoration:</p>
              <p className="text-gray-300 font-mono">धर्म संस्थापना वेताल शक्ति</p>
            </div>
            <div className="bg-black/20 rounded-lg p-3">
              <p className="text-yellow-400 font-semibold">Divine Intervention:</p>
              <p className="text-gray-300 font-mono">महावर बाबाजी आज्ञा वेताल सेवा</p>
            </div>
          </div>
        </div>
      </div>
        </>
      )}
    </div>
  );
};

export default VetalaProtectionDashboard;
