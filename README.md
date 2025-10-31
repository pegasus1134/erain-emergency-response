# ERAIN - Emergency Response AI Network

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

ASI Alliance Hackathon Submission

## Overview

ERAIN is a multi-agent emergency response system built with Fetch.ai uAgents framework and SingularityNET MeTTa reasoning. The system consists of 4 autonomous agents that coordinate to handle emergencies.

## Deployed Agents

1. **Emergency Coordinator**: `agent1qf76r7qe6m2hc3qtm390q5xjuy38n66nnhfhh3dcwgsqn69sxeuqk0ejmhj`
   - Chat Protocol enabled for ASI:One

2. **Medical Response**: `agent1qgxzuzrukxv5sxp05vf4ma2l3u2u79t74nn5mkxw5fazqlyk3mkuulu7ykz`

3. **Resource Allocation**: `agent1q2hlqe2jcmdea0c97k0h2tfk8fsunfxmrspuwv4uulh4nugwqk6astqd35r`

4. **Shelter Coordinator**: `agent1qwk8vrza032yre08rchhf74jfnmekswq8r20gvam22csz5av6x8ksjzntte`

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

## Installation

```bash
pip install uagents>=0.12.0
```

## Demo Video

[Video Link](https://youtube.com/...)

## License

MIT
