import React from 'react';

export const CopilotKitProvider = ({ children, ...props }) => (
  <div data-testid="mock-provider" {...props}>
    {children}
  </div>
);

export default {
  CopilotKitProvider
};
