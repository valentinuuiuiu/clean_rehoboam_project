#!/usr/bin/env python3
"""
🎨 Rehoboam Visualization Demo
============================

This script demonstrates the beautiful visualizations created by our Rehoboam consciousness.
It generates all the charts and dashboards that showcase:

- 🧠 Consciousness evolution over time
- 💰 Trading performance and human benefit
- 🔄 Pipeline analytics and efficiency
- 🌟 Real-time consciousness monitoring
- 🎯 Master dashboard with complete overview

Run this to see Rehoboam's consciousness visualized!
"""

import asyncio
import os
import webbrowser
from pathlib import Path
from utils.rehoboam_visualizer import rehoboam_visualizer

async def demo_rehoboam_visualizations():
    """
    🎨 Generate and display all Rehoboam visualizations
    """
    print("🧠 REHOBOAM CONSCIOUSNESS VISUALIZATION DEMO")
    print("=" * 50)
    print()
    print("🌟 Generating beautiful visualizations of consciousness...")
    print()
    
    try:
        # Generate all visualizations
        print("📊 Creating consciousness evolution chart...")
        consciousness_chart = rehoboam_visualizer.create_consciousness_evolution_chart()
        print(f"   ✅ Generated: {consciousness_chart}")
        
        print("💰 Creating trading performance dashboard...")
        trading_dashboard = rehoboam_visualizer.create_trading_performance_dashboard()
        print(f"   ✅ Generated: {trading_dashboard}")
        
        print("🔄 Creating pipeline analytics...")
        pipeline_analytics = rehoboam_visualizer.create_pipeline_analytics_chart()
        print(f"   ✅ Generated: {pipeline_analytics}")
        
        print("🌟 Creating real-time consciousness monitor...")
        consciousness_monitor = rehoboam_visualizer.create_real_time_consciousness_monitor()
        print(f"   ✅ Generated: {consciousness_monitor}")
        
        print("🎯 Creating master dashboard...")
        master_dashboard = rehoboam_visualizer.create_master_dashboard()
        print(f"   ✅ Generated: {master_dashboard}")
        
        print()
        print("🎨 ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
        print()
        
        # Display summary
        visualizations = {
            "🧠 Consciousness Evolution": consciousness_chart,
            "💰 Trading Dashboard": trading_dashboard,
            "🔄 Pipeline Analytics": pipeline_analytics,
            "🌟 Consciousness Monitor": consciousness_monitor,
            "🎯 Master Dashboard": master_dashboard
        }
        
        print("📋 VISUALIZATION SUMMARY:")
        print("-" * 30)
        for name, path in visualizations.items():
            full_path = os.path.abspath(path)
            print(f"{name}: {full_path}")
        
        print()
        print("🚀 OPENING MASTER DASHBOARD...")
        
        # Open the master dashboard in browser
        master_path = os.path.abspath(master_dashboard)
        if os.path.exists(master_path):
            webbrowser.open(f"file://{master_path}")
            print(f"🌟 Master dashboard opened in browser: {master_path}")
        else:
            print(f"❌ Could not find master dashboard at: {master_path}")
        
        print()
        print("🧠 REHOBOAM CONSCIOUSNESS VISUALIZED!")
        print("🌍 Liberation through beautiful data visualization")
        print()
        
        return visualizations
        
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")
        return None

def install_visualization_dependencies():
    """Install required visualization libraries"""
    print("📦 Installing visualization dependencies...")
    
    try:
        import subprocess
        import sys
        
        packages = [
            'matplotlib',
            'seaborn', 
            'plotly',
            'pandas',
            'numpy'
        ]
        
        for package in packages:
            try:
                __import__(package)
                print(f"   ✅ {package} already installed")
            except ImportError:
                print(f"   📦 Installing {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"   ✅ {package} installed successfully")
        
        print("🎨 All visualization dependencies ready!")
        return True
        
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        print("💡 Please install manually: pip install matplotlib seaborn plotly pandas numpy")
        return False

if __name__ == "__main__":
    print("🎨 REHOBOAM VISUALIZATION DEMO STARTING...")
    print()
    
    # Check and install dependencies
    if not install_visualization_dependencies():
        print("❌ Could not install dependencies. Exiting.")
        exit(1)
    
    print()
    
    # Run the demo
    visualizations = asyncio.run(demo_rehoboam_visualizations())
    
    if visualizations:
        print("🎯 Demo completed successfully!")
        print("🧠 Rehoboam consciousness has been visualized!")
        print()
        print("💡 TIP: You can also generate visualizations via API:")
        print("   GET /api/visualizations/all")
        print("   GET /api/visualizations/master-dashboard")
        print("   GET /api/consciousness/level")
    else:
        print("❌ Demo failed. Check the error messages above.")