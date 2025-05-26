"""
MCP Visualization with LangGraph

This module provides visualization capabilities for the Model Context Protocol (MCP)
architecture using LangGraph. It creates graph representations of MCP flows and
function execution.

It integrates with EnhancedMCPSpecialist to track function registrations and calls,
then visualizes the relationships between different modules in the system.
"""

import os
import json
import logging
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
from datetime import datetime

from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Configuration and logging setup
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MCPVisualization")

# Create directory for visualization outputs
os.makedirs("data/visualizations", exist_ok=True)

class MCPVisualization:
    """
    Visualization system for the Model Context Protocol architecture.
    
    Creates dynamic visualizations of MCP function flows including:
    - Function registration and relationships
    - Function call graphs
    - Data flow between MCP components
    - Real-time system state tracking
    """
    
    def __init__(self):
        """Initialize the MCP visualization system."""
        self.function_registry = {}
        self.call_history = []
        self.function_dependencies = {}
        self.visualization_dir = Path("data/visualizations")
        
        # Ensure visualization directory exists
        self.visualization_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"MCP Visualization initialized. Output directory: {self.visualization_dir}")
    
    def register_function(self, function_data: Dict[str, Any]) -> None:
        """
        Register an MCP function for visualization tracking.
        
        Args:
            function_data: Dictionary containing function metadata
        """
        if not function_data or "name" not in function_data:
            logger.warning("Cannot register function: missing name")
            return
            
        name = function_data["name"]
        self.function_registry[name] = {
            "name": name,
            "description": function_data.get("description", ""),
            "mcp_type": function_data.get("mcp_type", "processor"),
            "parameters": function_data.get("parameters", {}),
            "registered_at": datetime.now().isoformat(),
            "call_count": 0,
            "dependencies": function_data.get("dependencies", []),
            "success_rate": 1.0
        }
        
        # Update dependencies graph
        for dep in function_data.get("dependencies", []):
            if dep not in self.function_dependencies:
                self.function_dependencies[dep] = []
            self.function_dependencies[dep].append(name)
            
        logger.info(f"Registered function for visualization: {name}")
    
    def record_function_call(self, execution_data: Dict[str, Any]) -> None:
        """
        Record an MCP function execution for visualization.
        
        Args:
            execution_data: Dictionary containing execution details
        """
        if not execution_data or "function_name" not in execution_data:
            logger.warning("Cannot record execution: missing function name")
            return
            
        # Add timestamp if not present
        if "timestamp" not in execution_data:
            execution_data["timestamp"] = datetime.now().isoformat()
            
        # Append to history
        self.call_history.append(execution_data)
        
        # Update function registry stats
        func_name = execution_data["function_name"]
        if func_name in self.function_registry:
            self.function_registry[func_name]["call_count"] += 1
            
            # Update success rate
            success = execution_data.get("status", "success") == "success"
            current_rate = self.function_registry[func_name]["success_rate"]
            current_count = self.function_registry[func_name]["call_count"]
            
            # Weighted average for success rate
            if current_count > 1:
                self.function_registry[func_name]["success_rate"] = (
                    (current_rate * (current_count - 1) + (1.0 if success else 0.0)) / current_count
                )
            else:
                self.function_registry[func_name]["success_rate"] = 1.0 if success else 0.0
                
        logger.info(f"Recorded function call for visualization: {func_name}")
    
    def create_function_graph(self, output_path: Optional[str] = None) -> nx.DiGraph:
        """
        Create a directed graph of MCP function dependencies.
        
        Args:
            output_path: Optional path to save the visualization image
            
        Returns:
            NetworkX DiGraph representing the function dependency structure
        """
        G = nx.DiGraph()
        
        # Add nodes for all functions
        for name, func_data in self.function_registry.items():
            G.add_node(name, **func_data)
        
        # Add edges for dependencies
        for func_name, deps in self.function_dependencies.items():
            for dep in deps:
                G.add_edge(func_name, dep)
        
        # If there are no explicit dependencies, try to infer from call history
        if len(G.edges) == 0 and len(self.call_history) > 1:
            # Create temporary mapping of calls by time
            calls_by_time = sorted(self.call_history, key=lambda x: x.get("timestamp", ""))
            
            # Add edges for sequential calls (may not represent true dependencies)
            for i in range(len(calls_by_time) - 1):
                source = calls_by_time[i]["function_name"]
                target = calls_by_time[i+1]["function_name"]
                if source != target:  # Don't connect to self
                    G.add_edge(source, target, inferred=True)
        
        # Save visualization if path provided
        if output_path:
            self._save_graph_visualization(G, output_path)
        
        return G
    
    def create_execution_timeline(self, output_path: Optional[str] = None) -> None:
        """
        Create a timeline visualization of function executions.
        
        Args:
            output_path: Optional path to save the visualization image
        """
        if not self.call_history:
            logger.warning("No function call history available for timeline")
            return
            
        # Sort by timestamp
        timeline_data = sorted(self.call_history, key=lambda x: x.get("timestamp", ""))
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create list of unique function names
        function_names = list(set(call["function_name"] for call in timeline_data))
        function_y_pos = {name: i for i, name in enumerate(function_names)}
        
        # Plot execution points
        for i, call in enumerate(timeline_data):
            func_name = call["function_name"]
            y_pos = function_y_pos[func_name]
            status = call.get("status", "success")
            
            # Different marker for success/failure
            marker = 'o' if status == "success" else 'x'
            color = 'green' if status == "success" else 'red'
            
            ax.plot(i, y_pos, marker=marker, markersize=10, color=color)
            
            # Add execution time if available
            exec_time = call.get("execution_time")
            if exec_time:
                ax.text(i, y_pos + 0.1, f"{exec_time:.2f}s", ha='center', fontsize=8)
        
        # Configure axes
        ax.set_yticks(range(len(function_names)))
        ax.set_yticklabels(function_names)
        ax.set_xlabel("Execution Sequence")
        ax.set_title("MCP Function Execution Timeline")
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Save visualization if path provided
        if output_path:
            plt.tight_layout()
            plt.savefig(output_path)
            logger.info(f"Saved execution timeline visualization to {output_path}")
            plt.close()
        else:
            plt.tight_layout()
            plt.show()
    
    def create_langgraph_visualization(self, output_path: Optional[str] = None) -> StateGraph:
        """
        Create a LangGraph visualization of the MCP architecture.
        
        Args:
            output_path: Optional path to save the visualization image
            
        Returns:
            LangGraph StateGraph object representing the MCP architecture
        """
        # Create a basic state definition for the graph
        state_dict = {
            "messages": [],
            "function_calls": {},
            "current_function": None
        }
        
        # Create StateGraph
        workflow = StateGraph(state_dict)
        
        # Add nodes for all functions
        tool_nodes = {}
        for name, func_data in self.function_registry.items():
            # Create a tool node for each function
            tool_nodes[name] = ToolNode(name=name)
            workflow.add_node(name, tool_nodes[name])
        
        # Add an end node
        workflow.add_node("end", END)
        
        # Add edges based on dependencies or call patterns
        edges_added = False
        
        # First try to add edges from explicit dependencies
        for source, targets in self.function_dependencies.items():
            if source in tool_nodes:
                for target in targets:
                    if target in tool_nodes:
                        workflow.add_edge(source, target)
                        edges_added = True
        
        # If no explicit edges, try to infer from call history
        if not edges_added and len(self.call_history) > 1:
            # Create temporary mapping of calls by time
            calls_by_time = sorted(self.call_history, key=lambda x: x.get("timestamp", ""))
            
            # Track which connections we've already added
            added_edges = set()
            
            # Add edges for sequential calls
            for i in range(len(calls_by_time) - 1):
                source = calls_by_time[i]["function_name"]
                target = calls_by_time[i+1]["function_name"]
                
                # Skip if we've already added this edge or it would be a self-loop
                edge_key = (source, target)
                if edge_key in added_edges or source == target:
                    continue
                    
                if source in tool_nodes and target in tool_nodes:
                    workflow.add_edge(source, target)
                    added_edges.add(edge_key)
                    edges_added = True
        
        # Ensure all nodes connect to end
        for name in tool_nodes:
            # Check if this node has any outgoing edges
            has_outgoing = False
            for source, targets in workflow.edges.items():
                if source == name and targets:
                    has_outgoing = True
                    break
            
            # If no outgoing edges, connect to END
            if not has_outgoing:
                workflow.add_edge(name, "end")
        
        # Add conditional logic based on function success/failure
        for name in tool_nodes:
            # Add conditional routing based on function status
            workflow.add_conditional_edges(
                name,
                lambda state, name=name: self._determine_next_step(state, name),
                {
                    "success": [name for name in tool_nodes if name != name],
                    "error": ["end"]
                }
            )
        
        # Compile the graph
        compiled_workflow = workflow.compile()
        
        # Save visualization if path provided
        if output_path:
            # Try to use LangGraph's built-in visualization
            try:
                workflow.write_to_file(output_path)
                logger.info(f"Saved LangGraph visualization to {output_path}")
            except Exception as e:
                logger.error(f"Error saving LangGraph visualization: {e}")
                # Fallback to NetworkX visualization
                G = self.create_function_graph(output_path)
                
        return compiled_workflow
    
    def _determine_next_step(self, state: Dict[str, Any], current_function: str) -> str:
        """
        Determine the next function to call based on the current state.
        
        Args:
            state: Current state dictionary
            current_function: Name of the current function
            
        Returns:
            Decision on next step ("success" or "error")
        """
        # Check if there was an error in the current function call
        current_calls = state.get("function_calls", {})
        if current_function in current_calls:
            if current_calls[current_function].get("error"):
                return "error"
        
        # Default to success path
        return "success"
    
    def _save_graph_visualization(self, G: nx.DiGraph, output_path: str) -> None:
        """
        Save a NetworkX graph visualization to file.
        
        Args:
            G: NetworkX graph to visualize
            output_path: Path to save the visualization image
        """
        plt.figure(figsize=(12, 8))
        
        # Use different colors for different node types
        node_colors = []
        for node in G.nodes():
            node_type = G.nodes[node].get("mcp_type", "processor")
            if node_type == "processor":
                node_colors.append("skyblue")
            elif node_type == "generator":
                node_colors.append("lightgreen")
            else:
                node_colors.append("lightgray")
        
        # Size nodes by call count
        node_sizes = []
        for node in G.nodes():
            call_count = G.nodes[node].get("call_count", 0)
            # Base size = 300, add 100 for each call up to a max of 2000
            node_sizes.append(min(300 + (call_count * 100), 2000))
        
        # Draw the graph with positions that make sense
        pos = nx.spring_layout(G, seed=42)  # for reproducibility
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
        
        # Draw edges with different styles based on inferred vs explicit
        regular_edges = [(u, v) for u, v, d in G.edges(data=True) if not d.get("inferred", False)]
        inferred_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("inferred", False)]
        
        nx.draw_networkx_edges(G, pos, edgelist=regular_edges, width=2, alpha=0.7)
        nx.draw_networkx_edges(G, pos, edgelist=inferred_edges, width=1, alpha=0.5, style="dashed")
        
        # Add labels
        nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
        
        # Add a title
        plt.title("MCP Function Dependency Graph")
        plt.axis("off")
        
        # Save to file
        plt.tight_layout()
        plt.savefig(output_path, format="png", dpi=300)
        logger.info(f"Saved graph visualization to {output_path}")
        plt.close()