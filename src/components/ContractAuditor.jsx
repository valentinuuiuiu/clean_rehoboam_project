import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input'; // Assuming this is a styled input
import { Textarea } from './ui/textarea'; // Assuming this is a styled textarea
import { Label } from './ui/label';
import { useToast } from '../hooks/useToast'; // For notifications

const ContractAuditor = () => {
  const [contractCode, setContractCode] = useState('');
  const [auditTaskDescription, setAuditTaskDescription] = useState('');
  const [auditResult, setAuditResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const { toast } = useToast();

  const API_BASE_URL = import.meta.env.VITE_API_URL || '';

  const handleAuditSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setAuditResult(null);

    if (!contractCode.trim()) {
      setError("Contract code cannot be empty.");
      setIsLoading(false);
      toast({ title: "Input Error", description: "Contract code is required.", variant: "destructive" });
      return;
    }
    if (!auditTaskDescription.trim()) {
      setError("Audit task description cannot be empty.");
      setIsLoading(false);
      toast({ title: "Input Error", description: "Audit task description is required.", variant: "destructive" });
      return;
    }

    const payload = {
      contract_code: contractCode,
      audit_task_description: auditTaskDescription,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/audit/contract`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // TODO: Add Authorization header if required by your get_current_user dependency
          // 'Authorization': `Bearer ${your_auth_token_here}`
        },
        body: JSON.stringify(payload),
      });

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(responseData.detail || responseData.error?.detail || `HTTP error ${response.status}`);
      }

      setAuditResult(responseData);
      toast({ title: "Audit Submitted", description: "Audit request processed successfully.", variant: "success" });

    } catch (err) {
      console.error("Audit request failed:", err);
      setError(err.message || "Failed to submit audit request. Check console for details.");
      toast({ title: "Audit Failed", description: err.message, variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 space-y-8">
      <Card className="bg-gray-800 border-gray-700 shadow-xl">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-blue-300">AI Smart Contract Auditor</CardTitle>
          <CardDescription className="text-gray-400">
            Submit your Solidity contract code and describe the audit task you want the AI to perform.
            The AI will leverage T2L-inspired dynamic specialization for the audit.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAuditSubmit} className="space-y-6">
            <div>
              <Label htmlFor="contractCode" className="block text-sm font-medium text-gray-300 mb-1">
                Solidity Contract Code
              </Label>
              <Textarea
                id="contractCode"
                value={contractCode}
                onChange={(e) => setContractCode(e.target.value)}
                placeholder="Paste your Solidity contract code here..."
                className="w-full h-64 bg-gray-900 text-gray-200 border-gray-600 focus:ring-blue-500 focus:border-blue-500 rounded-md p-2 font-mono text-sm"
                required
              />
            </div>
            <div>
              <Label htmlFor="auditTaskDescription" className="block text-sm font-medium text-gray-300 mb-1">
                Audit Task Description
              </Label>
              <Input
                id="auditTaskDescription"
                type="text"
                value={auditTaskDescription}
                onChange={(e) => setAuditTaskDescription(e.target.value)}
                placeholder="e.g., 'Check for reentrancy vulnerabilities and gas optimizations'"
                className="w-full bg-gray-900 text-gray-200 border-gray-600 focus:ring-blue-500 focus:border-blue-500 rounded-md p-2"
                required
              />
            </div>
            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-500 text-white font-semibold py-2 px-4 rounded-md"
            >
              {isLoading ? 'Auditing...' : 'Submit for AI Audit'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {isLoading && (
        <div className="text-center p-4">
          <p className="text-lg text-purple-400 animate-pulse">Auditing contract, please wait...</p>
        </div>
      )}

      {error && (
        <Card className="bg-red-900/30 border-red-700">
          <CardHeader>
            <CardTitle className="text-red-400">Audit Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-300 whitespace-pre-wrap">{error}</p>
          </CardContent>
        </Card>
      )}

      {auditResult && auditResult.status === 'success' && (
        <Card className="bg-gray-800 border-gray-700 shadow-lg mt-6">
          <CardHeader>
            <CardTitle className="text-xl text-green-400">Audit Results</CardTitle>
            <CardDescription className="text-gray-400">
              Task: {auditResult.audit_task} (Source: {auditResult.source_description || 'N/A'})
            </CardDescription>
          </CardHeader>
          <CardContent>
            <h4 className="text-lg font-semibold text-gray-200 mb-2">Detailed Findings:</h4>
            <div className="p-3 bg-gray-900 rounded max-h-[600px] overflow-y-auto">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap break-all">
                {JSON.stringify(auditResult.audit_result, null, 2)}
              </pre>
            </div>
             <p className="text-xs text-gray-500 mt-4">Timestamp: {new Date(auditResult.timestamp).toLocaleString()}</p>
          </CardContent>
        </Card>
      )}
      {auditResult && auditResult.status !== 'success' && (
         <Card className="bg-yellow-900/30 border-yellow-700">
         <CardHeader>
           <CardTitle className="text-yellow-400">Audit Information</CardTitle>
         </CardHeader>
         <CardContent>
           <p className="text-yellow-300">Status: {auditResult.status}</p>
           <pre className="text-sm text-yellow-200 whitespace-pre-wrap break-all mt-2">
             {JSON.stringify(auditResult, null, 2)}
           </pre>
         </CardContent>
       </Card>
      )}
    </div>
  );
};

export default ContractAuditor;
