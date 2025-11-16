# Render MCP Setup for Claude Code

This guide will help you add the Render MCP (Model Context Protocol) to your local Claude Code installation so you can manage Render services directly from Claude Code.

## Prerequisites

- Claude Code installed and configured
- Node.js and npm installed
- A Render account (https://render.com)

## Step 1: Get Your Render API Key

1. Open https://dashboard.render.com/u/settings#api-keys in your browser
2. Click **"Create API Key"**
3. Give it a name like `Claude Code MCP`
4. Copy the API key (it will start with `rnd_`)
5. **Important:** Save this key somewhere safe - you won't be able to see it again!

## Step 2: Add Render MCP to Claude Code

Run this command in your terminal, replacing `YOUR_API_KEY_HERE` with your actual Render API key:

```bash
claude mcp add render \
  --package-name @render.com/mcp-server-render \
  --env RENDER_API_KEY=YOUR_API_KEY_HERE
```

Example with a fake API key:
```bash
claude mcp add render \
  --package-name @render.com/mcp-server-render \
  --env RENDER_API_KEY=rnd_abc123xyz456...
```

## Step 3: Verify Installation

Check that the MCP was added successfully:

```bash
claude mcp list
```

You should see `render` in the list of configured MCP servers.

## Step 4: Restart Claude Code

Restart Claude Code to load the new MCP server:

```bash
# Close any running Claude Code sessions
# Then start a new session
```

## What You Can Do With Render MCP

Once configured, you can use Claude Code to:

- **List all services**: View all your Render web services, workers, and databases
- **Deploy services**: Trigger new deployments
- **Manage environment variables**: Add, update, or remove env vars
- **View logs**: Stream and search service logs
- **Create services**: Set up new web services, databases, etc.
- **Monitor deployments**: Check deployment status and history
- **Manage PostgreSQL**: Create databases, run queries, check metrics

## Example Prompts to Try

Once the MCP is configured, try these prompts in Claude Code:

```
"List all my Render services"
"Show me the logs for my agent-platform-backend service"
"Update the GEMINI_API_KEY environment variable"
"Create a new PostgreSQL database"
"Show me the deployment history for my backend"
```

## Troubleshooting

### MCP not showing up
- Make sure you restarted Claude Code after adding the MCP
- Verify your API key is correct: `claude mcp list`

### Permission errors
- Check that your Render API key has the necessary permissions
- You can create a new API key if needed

### Connection issues
- Ensure you have internet connection
- Verify the Render API is accessible: https://api.render.com

## Current Services (from your account)

These are the services currently available in your Render account:

1. **agent-platform-backend**
   - URL: https://agent-platform-backend-3g16.onrender.com
   - Type: Docker web service
   - Purpose: Agent Management Platform API

2. **wildfire-simulator-v2**
   - URL: https://wildfire-simulator-v2.onrender.com
   - Type: Docker web service

3. **wildfire-api-v2**
   - URL: https://wildfire-api-v2.onrender.com
   - Type: Python web service

4. **wildfire-db** (PostgreSQL)
   - Database: wildfire
   - User: wildfire_user
   - Plan: Free tier

## Additional Resources

- Render MCP Documentation: https://github.com/renderinc/mcp-server-render
- Render API Docs: https://api-docs.render.com
- Claude Code MCP Guide: https://docs.claude.com/claude-code

## Security Notes

- Never commit your Render API key to git
- Store it securely in your password manager
- Rotate keys periodically for security
- Use separate API keys for different environments (dev/prod)
