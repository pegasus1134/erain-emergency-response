# ERAIN - Emergency Response AI Network

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

ASI Alliance Hackathon Submission

## Overview

ERAIN is a multi-agent emergency response system built with Fetch.ai uAgents framework and SingularityNET MeTTa reasoning. The system consists of 4 autonomous agents that coordinate to handle emergencies.

## Deployed Agents

1. **Emergency Coordinator**: `agent1qfvx3gqgpngs7n8n5gjqh3ey0z9fee4wn2nz6r9g0glrqeu5stark6kpqzx`
   - Chat Protocol enabled for ASI:One

2. **Medical Response**: `agent1qf4au6rzaauxhy2jze5v5tl8zct2g0cfg0qx8hfhcm3mq0dqzmguz5u4w7m`

3. **Resource Allocation**: `agent1qwr7920pvzp8gtz8c6em6ezqkl0hqe0tttc0q6ze6ljew4yc0lzxc3lv9gp`

4. **Shelter Coordinator**: `agent1qg7cy6z7xjrvxfqwn7qhss6wyqnthqc5qhhvnearv9c0ctxzl8q2vfn0dy5`

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
