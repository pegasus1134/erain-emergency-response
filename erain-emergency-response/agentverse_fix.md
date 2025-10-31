# Fix ASI:One Integration on Agentverse

## Go to your agent on Agentverse and update these:

### 1. In the "Overview" Tab:
- **Name**: ERAIN Emergency Coordinator
- **Description**: Emergency response coordinator for disaster management. Report emergencies in natural language.

### 2. In the "SEO Interactions" Tab:
- **Search Visibility**: Make sure it's ON/ENABLED
- **Keywords**: emergency, disaster, help, fire, flood, accident, ERAIN
- **Public**: Yes

### 3. In the "Domains" Tab:
- Make sure it says "chat" or "communication"
- Enable "Public Discovery"

### 4. In the "Build" Tab, make sure these lines are at the end:
```python
# Include chat protocol - MUST BE LAST
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
```

### 5. After making changes:
1. Click "Save" or "Update"
2. Click "Deploy" or "Redeploy"
3. Wait for "Deployment Successful"
4. Click "Restart Agent"
5. Check logs show: "✅ Chat Protocol: ENABLED for ASI:One"

### 6. Wait 2-3 minutes for ASI:One to index your agent

### 7. Then on ASI:One try:
- Search: "ERAIN Emergency"
- Or click "Browse Agents" and filter by "Emergency"
- Or use: /discover emergency

## If Still Not Working:

The agent might need to be re-registered with ASI:One. On Agentverse:
1. Toggle the agent to INACTIVE
2. Wait 30 seconds
3. Toggle back to ACTIVE
4. This forces re-registration with ASI:One

## Test Message Once Connected:
"Fire at downtown building, 10 people injured, need immediate help"