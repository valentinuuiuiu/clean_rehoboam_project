import React, { Component } from 'react';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error(`Error in ${this.props.section || 'component'}:`, error);
    console.error('Error details:', errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 shadow-lg">
          <h3 className="text-lg font-semibold text-red-400 mb-2">
            {this.props.section ? `Error in ${this.props.section}` : 'Something went wrong'}
          </h3>
          <div className="bg-black/50 p-3 rounded font-mono text-sm text-red-300 overflow-auto max-h-48 mb-3">
            {this.state.error && this.state.error.toString()}
          </div>
          <button
            className="px-4 py-2 bg-red-700 text-white rounded hover:bg-red-600"
            onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })}
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;