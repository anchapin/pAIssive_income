import React from 'react';
import { CopilotKitProvider } from '@copilotkit/react-core';
import { CopilotTextarea } from '@copilotkit/react-ui';

/**
 * CopilotKitIntegration component that demonstrates integration with CopilotKit
 * This is a simple example that shows how to use CopilotKit in a React application
 */
const CopilotKitIntegration = () => {
  return (
    <div data-testid="copilot-integration-container" className="p-4 bg-gray-100 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">CopilotKit Integration Demo</h2>
      
      <CopilotKitProvider>
        <div className="mb-4">
          <p className="mb-2">Try typing in the textarea below and ask for help:</p>
          <CopilotTextarea
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="Type here and ask for help..."
            copilotContext={{
              recentMessages: [],
              systemPrompt: "You are a helpful assistant that helps users with their tasks."
            }}
          />
        </div>
        
        <div className="mt-4 p-3 bg-blue-50 rounded border border-blue-200">
          <h3 className="text-lg font-semibold mb-2">How to use:</h3>
          <ol className="list-decimal pl-5">
            <li>Type in the textarea above</li>
            <li>Ask for help with a task</li>
            <li>The AI will respond with helpful suggestions</li>
          </ol>
        </div>
      </CopilotKitProvider>
    </div>
  );
};

export default CopilotKitIntegration;
