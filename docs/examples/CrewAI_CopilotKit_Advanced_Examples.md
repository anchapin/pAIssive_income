# Advanced CrewAI + CopilotKit Integration Examples

This document provides advanced examples of integrating CrewAI with CopilotKit to create powerful AI-driven applications.

## End-to-End Workflow Example

This example demonstrates how to create an end-to-end workflow that connects a CopilotKit frontend with a CrewAI backend.

### Backend (Flask API)

```python
from flask import Flask, request, jsonify
from agent_team.crewai_agents import CrewAIAgentTeam
from langchain.llms import OpenAI

app = Flask(__name__)

@app.route('/api/crewai/content-generation', methods=['POST'])
def generate_content():
    """
    API endpoint for content generation using CrewAI.
    
    Expected request body:
    {
        "topic": "Topic to generate content about",
        "content_type": "blog|article|social",
        "target_audience": "Description of the target audience",
        "length": "short|medium|long"
    }
    """
    try:
        data = request.json
        
        # Initialize LLM provider
        llm = OpenAI(api_key="your-api-key")
        
        # Create a CrewAI agent team
        agent_team = CrewAIAgentTeam(llm_provider=llm)
        
        # Add specialized agents
        agent_team.add_agent(
            role="Researcher",
            goal="Research the topic thoroughly",
            backstory="Expert researcher with access to vast knowledge"
        )
        
        agent_team.add_agent(
            role="Content Strategist",
            goal="Develop a content strategy for the target audience",
            backstory="Experienced content strategist who understands audience needs"
        )
        
        agent_team.add_agent(
            role="Writer",
            goal="Create engaging content based on research and strategy",
            backstory="Professional writer with expertise in various content formats"
        )
        
        agent_team.add_agent(
            role="Editor",
            goal="Ensure content quality and consistency",
            backstory="Detail-oriented editor with a keen eye for quality"
        )
        
        # Add tasks
        agent_team.add_task(
            description=f"Research the topic: {data['topic']}",
            agent="Researcher"
        )
        
        agent_team.add_task(
            description=f"Develop a content strategy for {data['target_audience']}",
            agent="Content Strategist"
        )
        
        agent_team.add_task(
            description=f"Write {data['length']} {data['content_type']} about {data['topic']}",
            agent="Writer"
        )
        
        agent_team.add_task(
            description="Edit and finalize the content",
            agent="Editor"
        )
        
        # Run the workflow
        result = agent_team.run()
        
        return jsonify({
            "status": "success",
            "content": result
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Frontend (React)

```jsx
import React, { useState } from 'react';
import { CopilotKitProvider } from '@copilotkit/react-core';
import { CopilotChat, useCopilotAction } from '@copilotkit/react-ui';

// Custom tool for content generation
function ContentGenerationTool() {
  useCopilotAction({
    name: "generate_content",
    description: "Generate content using AI agents",
    parameters: [
      {
        name: "topic",
        type: "string",
        description: "The topic to generate content about"
      },
      {
        name: "content_type",
        type: "string",
        description: "The type of content (blog, article, social)",
        enum: ["blog", "article", "social"]
      },
      {
        name: "target_audience",
        type: "string",
        description: "Description of the target audience"
      },
      {
        name: "length",
        type: "string",
        description: "The length of the content",
        enum: ["short", "medium", "long"]
      }
    ],
    handler: async ({ topic, content_type, target_audience, length }) => {
      try {
        const response = await fetch('/api/crewai/content-generation', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            topic, 
            content_type, 
            target_audience, 
            length 
          })
        });
        
        if (!response.ok) {
          throw new Error('Failed to generate content');
        }
        
        const data = await response.json();
        return data.content;
      } catch (error) {
        console.error('Error generating content:', error);
        return `Error: ${error.message}`;
      }
    }
  });
  
  return null;
}

// Content generation application
function ContentGenerationApp() {
  const [generatedContent, setGeneratedContent] = useState('');
  
  return (
    <CopilotKitProvider>
      <div className="app-container">
        <h1>AI Content Generator</h1>
        
        <div className="content-display">
          {generatedContent ? (
            <div className="generated-content">
              <h2>Generated Content</h2>
              <div dangerouslySetInnerHTML={{ __html: generatedContent }} />
            </div>
          ) : (
            <div className="placeholder">
              <p>Generated content will appear here</p>
            </div>
          )}
        </div>
        
        <div className="chat-container">
          <ContentGenerationTool />
          <CopilotChat
            instructions={`
              You are a content generation assistant. You can help users generate various types of content.
              
              To generate content, ask the user for:
              1. The topic they want content about
              2. The type of content (blog, article, social post)
              3. Their target audience
              4. The desired length (short, medium, long)
              
              Then use the generate_content tool to create the content.
            `}
            onMessageResponse={(message) => {
              // Check if the message contains generated content
              if (message.includes("Here's your generated content:")) {
                const contentStart = message.indexOf("Here's your generated content:") + 
                  "Here's your generated content:".length;
                const content = message.substring(contentStart).trim();
                setGeneratedContent(content);
              }
            }}
          />
        </div>
      </div>
    </CopilotKitProvider>
  );
}

export default ContentGenerationApp;
```

## Best Practices for Production Deployment

When deploying CrewAI + CopilotKit to production, consider the following best practices:

1. **API Key Management**: Store API keys securely using environment variables or a secrets manager
2. **Error Handling**: Implement comprehensive error handling on both frontend and backend
3. **Rate Limiting**: Add rate limiting to prevent abuse of AI services
4. **Caching**: Implement caching for common queries to reduce API calls
5. **Monitoring**: Set up monitoring for API calls, response times, and error rates
6. **Fallbacks**: Provide fallback mechanisms when AI services are unavailable
7. **User Feedback**: Collect user feedback to improve the AI experience
8. **Testing**: Thoroughly test with different inputs and edge cases

## Additional Resources

- [CrewAI Advanced Usage Guide](https://docs.crewai.com/advanced-usage/)
- [CopilotKit Custom Tools Documentation](https://docs.copilotkit.ai/custom-tools)
- [End-to-End Testing Strategies](https://docs.copilotkit.ai/testing)
- [Performance Optimization Guide](https://docs.copilotkit.ai/performance)
