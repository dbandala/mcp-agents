import { MCPConfiguration } from "@mastra/mcp";
import { Agent } from "@mastra/core/agent";
import { openai } from "@ai-sdk/openai";

const mcp = new MCPConfiguration({
  servers: {
    stockPrice: {
      command: "npx",
      args: ["tsx", "stock-price.ts"],
      env: {
        API_KEY: "your-api-key",
      },
    },
    weather: {
      url: new URL("http://localhost:8080/sse"),
    },
  },
});

// Create an agent with access to all tools
const agent = new Agent({
  name: "Multi-tool Agent",
  instructions: "You have access to multiple tool servers.",
  model: openai("gpt-4"),
  tools: await mcp.getTools(),
});