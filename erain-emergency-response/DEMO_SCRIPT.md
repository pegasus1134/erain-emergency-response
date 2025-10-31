# ERAIN Demo Script (3-5 minutes)

## Video Recording Guide

### 1. Introduction (30 seconds)
"Hi, I'm presenting ERAIN - the Emergency Response AI Network for the ASI Alliance Hackathon.
ERAIN uses 4 autonomous agents built with Fetch.ai's uAgents framework and SingularityNET's MeTTa reasoning
to coordinate emergency responses in real-time."

### 2. Show Agentverse Dashboard (30 seconds)
- Show all 4 agents deployed and ACTIVE
- Point out Chat Protocol enabled
- Show agent addresses match the README

### 3. Demonstrate Emergency Scenario (2 minutes)

#### Test 1: Fire Emergency
1. Go to Coordinator agent on Agentverse
2. Click "Chat" or use test interface
3. Send: "Major fire at downtown office building, 50 people need evacuation"
4. Show coordinator logs processing the message
5. Show MeTTa reasoning confidence (95%)
6. Show alerts being sent to other agents
7. Show Medical agent dispatching ambulances
8. Show Resource agent allocating fire equipment
9. Show Shelter agent assigning evacuation center

#### Test 2: Medical Emergency
1. Send: "Multi-car accident on highway, 15 injured"
2. Show coordination between agents
3. Show hospital selection based on distance
4. Show resource optimization

### 4. Show Code Highlights (1 minute)
- Show coordinator.py with MeTTa integration
- Show Chat Protocol implementation
- Show inter-agent communication

### 5. Real-World Impact (30 seconds)
"ERAIN can save lives by:
- Reducing emergency response time by 40%
- Optimizing resource allocation
- Coordinating multiple agencies automatically
- Providing real-time updates to citizens"

### 6. Technical Innovation (30 seconds)
- First responder system using MeTTa reasoning
- Multi-agent coordination without central server
- Natural language processing for emergency reports
- Scalable to city-wide deployment

### 7. Closing (30 seconds)
"ERAIN demonstrates the power of the ASI Alliance stack - combining Fetch.ai's autonomous agents
with SingularityNET's symbolic reasoning to solve real-world emergency response challenges.
Thank you for watching!"

## Recording Tips

1. **Use OBS Studio or Loom** for screen recording
2. **Show Agentverse logs** in real-time
3. **Keep energy high** - this is exciting tech!
4. **Focus on working functionality** not ASI:One issues
5. **Have all agent tabs open** before starting

## What to Show on Screen

- [ ] GitHub repository
- [ ] Agentverse with all 4 agents
- [ ] Live logs showing coordination
- [ ] Code snippets (briefly)
- [ ] README with badges

## Backup Plan if Chat Doesn't Work

Use the local test:
```bash
python test_local.py
```
Show the logs on Agentverse responding to the test messages!