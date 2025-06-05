import React from 'react';
import VetalaProtectionDashboard from './src/components/VetalaProtectionDashboard.jsx';

// Simple test to verify VetalaProtectionDashboard renders
console.log('Testing VetalaProtectionDashboard component...');

try {
    // Check if the component can be imported
    console.log('✅ VetalaProtectionDashboard imported successfully');
    console.log('Component:', typeof VetalaProtectionDashboard);
    
    // Check if the required services are available
    import('./src/services/consciousness/vetalaProtectionService.js').then(() => {
        console.log('✅ vetalaProtectionService imported successfully');
    }).catch(e => {
        console.error('❌ vetalaProtectionService import failed:', e.message);
    });
    
} catch (error) {
    console.error('❌ Component test failed:', error.message);
}
