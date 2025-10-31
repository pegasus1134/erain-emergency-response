# ERAIN - Emergency Response AI Network

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

ASI Alliance Hackathon Submission

## Overview

ERAIN is a multi-agent emergency response system built with Fetch.ai uAgents framework and SingularityNET MeTTa reasoning. The system consists of 4 autonomous agents that coordinate to handle emergencies.

## Deployed Agents on Agentverse

All agents are registered on Agentverse with Chat Protocol enabled for ASI:One integration.

1. **Emergency Coordinator**: `agent1qf76r7qe6m2hc3qtm390q5xjuy38n66nnhfhh3dcwgsqn69sxeuqk0ejmhj`
   - Name: ERAIN Emergency Coordinator
   - Role: Main orchestrator, receives emergencies via Chat Protocol
   - Chat Protocol: ✅ Enabled for ASI:One

2. **Medical Response**: `agent1qgxzuzrukxv5sxp05vf4ma2l3u2u79t74nn5mkxw5fazqlyk3mkuulu7ykz`
   - Name: Medical Response Agent
   - Role: Dispatches ambulances and coordinates hospitals

3. **Resource Allocation**: `agent1q2hlqe2jcmdea0c97k0h2tfk8fsunfxmrspuwv4uulh4nugwqk6astqd35r`
   - Name: Resource Allocation Agent
   - Role: Manages emergency supplies and equipment

4. **Shelter Coordinator**: `agent1qwk8vrza032yre08rchhf74jfnmekswq8r20gvam22csz5av6x8ksjzntte`
   - Name: Shelter Coordinator Agent
   - Role: Assigns evacuation centers and manages capacity

## Features

- Natural language emergency reporting via ASI:One
- Multi-agent coordination
- MeTTa reasoning for emergency analysis
- Resource optimization

## Project Structure

```
erain-emergency-response/
├── agents/
│   ├── coordinator.py
│   ├── medical.py
│   ├── resource.py
│   └── shelter.py
├── knowledge/
│   └── emergency_knowledge_graph.py
└── configs/
```

## Try It

1. Go to [ASI:One](https://asi.one)
2. Search "Emergency Coordinator ERAIN"
3. Report an emergency

## Requirements & Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Install Dependencies
```bash
# Install uAgents framework
pip install uagents>=0.12.0

# Install MeTTa for knowledge reasoning
pip install hyperon

# Install additional requirements
pip install cosmpy requests
```

### Run the Agents
```bash
# Each agent runs independently
python agents/coordinator.py
python agents/medical.py
python agents/resource.py
python agents/shelter.py
```

## Testing

### Option 1: Test via Agentverse Chat
1. Go to [Agentverse](https://agentverse.ai)
2. Navigate to any agent
3. Use the Chat feature to send test messages

### Option 2: Local Testing
```bash
python test_local.py
```

## Demo Video

[Watch Demo - ASI:One Working!](https://www.loom.com/share/971f6001392d46d7aef842b8560c965a)

## License

MIT
