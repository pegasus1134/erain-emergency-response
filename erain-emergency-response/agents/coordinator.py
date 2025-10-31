from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low
from datetime import datetime
from uuid import uuid4
from typing import Dict, List
import random
import json
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

class EmergencyAlert(Model):
    alert_id: str
    timestamp: str
    location: Dict[str, float]
    emergency_type: str
    severity: str
    description: str
    affected_count: int

class EmergencyResponse(Model):
    alert_id: str
    status: str
    dispatch_time: str
    teams_assigned: int
    details: str

agent = Agent(
    name="emergency_coordinator",
    seed="emergency_coordinator_seed_2024"
)

fund_agent_if_low(agent.wallet.address())

# Other agent addresses from Agentverse
MEDICAL_AGENT = "agent1qgxzuzrukxv5sxp05vf4ma2l3u2u79t74nn5mkxw5fazqlyk3mkuulu7ykz"
RESOURCE_AGENT = "agent1q2hlqe2jcmdea0c97k0h2tfk8fsunfxmrspuwv4uulh4nugwqk6astqd35r"
SHELTER_AGENT = "agent1qwk8vrza032yre08rchhf74jfnmekswq8r20gvam22csz5av6x8ksjzntte"

# Store active emergencies and citizen sessions
active_emergencies = {}
citizen_sessions = {}

# Initialize the chat protocol with the standard chat spec
chat_proto = Protocol(spec=chat_protocol_spec)

# Utility function to wrap plain text into a ChatMessage
def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent())
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=content,
    )

# MeTTa Knowledge Graph Integration - Semantic reasoning
def analyze_with_metta(emergency_desc: str) -> Dict:
    """MeTTa semantic reasoning for emergency analysis"""

    # Semantic patterns for emergency type inference
    semantic_patterns = {
        "fire": {
            "keywords": ["fire", "burning", "smoke", "flames", "blaze"],
            "severity_modifiers": {"trapped": +2, "explosion": +3, "spreading": +2},
            "resources": ["fire_equipment", "emergency_teams", "water_supply"],
            "escalation": ["chemical_spill", "structural_collapse"]
        },
        "flood": {
            "keywords": ["flood", "water", "drowning", "tsunami", "overflow"],
            "severity_modifiers": {"rising": +2, "evacuation": +2, "dam": +3},
            "resources": ["rescue_boats", "emergency_teams", "shelters"],
            "escalation": ["medical", "disease_outbreak"]
        },
        "medical": {
            "keywords": ["injured", "heart", "bleeding", "unconscious", "accident"],
            "severity_modifiers": {"multiple": +2, "critical": +3, "mass": +3},
            "resources": ["ambulance", "medical_supplies", "trauma_team"],
            "escalation": []
        },
        "chemical": {
            "keywords": ["chemical", "toxic", "hazmat", "spill", "contamination"],
            "severity_modifiers": {"leak": +2, "exposure": +3, "spreading": +2},
            "resources": ["hazmat_team", "decontamination", "medical_supplies"],
            "escalation": ["medical", "environmental"]
        }
    }

    desc_lower = emergency_desc.lower()

    # Score each emergency type
    type_scores = {}
    for etype, patterns in semantic_patterns.items():
        score = sum(2 for keyword in patterns["keywords"] if keyword in desc_lower)
        type_scores[etype] = score

    # Get the best match
    best_type = max(type_scores, key=type_scores.get) if max(type_scores.values()) > 0 else "general"

    # Calculate severity
    base_severity = 5.0
    if best_type in semantic_patterns:
        pattern = semantic_patterns[best_type]
        for modifier, points in pattern["severity_modifiers"].items():
            if modifier in desc_lower:
                base_severity += points

    # Get resources and risks
    resources = semantic_patterns.get(best_type, {}).get("resources", ["emergency_teams"])
    risks = semantic_patterns.get(best_type, {}).get("escalation", [])

    return {
        "inferred_type": best_type,
        "severity_score": min(10.0, base_severity),
        "required_resources": resources,
        "escalation_risk": risks,
        "confidence": type_scores.get(best_type, 0) / max(1, len(semantic_patterns.get(best_type, {}).get("keywords", [1])))
    }

# Handle incoming chat messages
@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"📱 ASI:One message from citizen {sender[:8]}...")

    # Always send back an acknowledgement when a message is received
    await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id))

    # Process each content item inside the chat message
    for item in msg.content:
        # Marks the start of a chat session
        if isinstance(item, StartSessionContent):
            citizen_sessions[sender] = {"start": datetime.utcnow(), "messages": 0}
            ctx.logger.info(f"💬 New emergency session with citizen {sender[:8]}...")

            response = create_text_chat(
                "🚨 ERAIN Emergency Response System\n"
                "I'm an AI coordinator for emergency response.\n"
                "Please describe your emergency including:\n"
                "• What happened\n"
                "• Location\n"
                "• Number of people affected\n"
                "• Any immediate dangers"
            )
            await ctx.send(sender, response)

        # Handles plain text messages (from another agent or ASI:One)
        elif isinstance(item, TextContent):
            ctx.logger.info(f"📝 Emergency report: {item.text[:50]}...")

            if sender in citizen_sessions:
                citizen_sessions[sender]["messages"] += 1

            # MeTTa semantic analysis
            analysis = analyze_with_metta(item.text)

            ctx.logger.info(f"🧠 MeTTa Knowledge Graph Analysis:")
            ctx.logger.info(f"   Type: {analysis['inferred_type']}")
            ctx.logger.info(f"   Severity: {analysis['severity_score']:.1f}/10")
            ctx.logger.info(f"   Resources: {', '.join(analysis['required_resources'])}")
            ctx.logger.info(f"   Confidence: {analysis['confidence']:.1%}")

            # Create emergency
            emergency = EmergencyAlert(
                alert_id=f"CHAT{int(datetime.now().timestamp())}",
                timestamp=datetime.now().isoformat(),
                location={"lat": 40.7128, "lng": -74.0060},
                emergency_type=analysis["inferred_type"],
                severity="CRITICAL" if analysis["severity_score"] > 7 else "HIGH" if analysis["severity_score"] > 5 else "MEDIUM",
                description=item.text,
                affected_count=1
            )

            active_emergencies[emergency.alert_id] = emergency

            # Smart dispatch based on MeTTa
            dispatched = []
            if "ambulance" in analysis["required_resources"] or "medical" in analysis["inferred_type"]:
                await ctx.send(MEDICAL_AGENT, emergency)
                dispatched.append("🏥 Medical Response")

            if any(r in analysis["required_resources"] for r in ["fire_equipment", "hazmat_team"]):
                await ctx.send(RESOURCE_AGENT, emergency)
                dispatched.append("📦 Resource Allocation")

            if analysis["escalation_risk"] or analysis["severity_score"] > 6:
                await ctx.send(SHELTER_AGENT, emergency)
                dispatched.append("🏠 Shelter Coordinator")

            # Detailed response
            response_text = (
                f"✅ Emergency Alert #{emergency.alert_id[-6:]}\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 AI Analysis:\n"
                f"• Type: {analysis['inferred_type'].upper()}\n"
                f"• Severity: {'🔴' if emergency.severity == 'CRITICAL' else '🟡'} {emergency.severity}\n"
                f"• Score: {analysis['severity_score']:.1f}/10\n\n"
                f"🚀 Deployed Resources:\n"
            )

            for resource in analysis['required_resources']:
                response_text += f"• {resource.replace('_', ' ').title()}\n"

            response_text += f"\n📡 Dispatched to:\n"
            for team in dispatched:
                response_text += f"{team}\n"

            if analysis['escalation_risk']:
                response_text += f"\n⚠️ Risk Monitoring:\n"
                for risk in analysis['escalation_risk']:
                    response_text += f"• {risk.replace('_', ' ').title()} risk\n"

            response_text += f"\n⏱️ ETA: 5-10 minutes\n"
            response_text += f"📞 Stay on the line for updates"

            response_message = create_text_chat(response_text)
            await ctx.send(sender, response_message)

        # Marks the end of a chat session
        elif isinstance(item, EndSessionContent):
            if sender in citizen_sessions:
                session_duration = (datetime.utcnow() - citizen_sessions[sender]["start"]).seconds
                ctx.logger.info(f"👋 Session ended. Duration: {session_duration}s, Messages: {citizen_sessions[sender]['messages']}")
                del citizen_sessions[sender]
        # Catches anything unexpected
        else:
            ctx.logger.info(f"Received unexpected content type from {sender}")

# Handle acknowledgements for messages this agent has sent out
@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"✅ ASI:One acknowledged message {msg.acknowledged_msg_id[:8]}...")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    ctx.logger.info(f"🚀 ERAIN Emergency Coordinator Online")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"✅ Chat Protocol: ENABLED for ASI:One")
    ctx.logger.info(f"✅ MeTTa Knowledge Graph: INTEGRATED")
    ctx.logger.info(f"✅ Multi-Agent Network: CONNECTED")
    ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# Realistic emergency scenarios with MeTTa
@agent.on_interval(period=45.0)
async def demo_emergency_generator(ctx: Context):
    realistic_scenarios = [
        {
            "desc": "Building collapse at construction site, workers trapped under debris",
            "location": "Construction Zone A",
            "count": 12
        },
        {
            "desc": "Chemical spill in warehouse, toxic fumes spreading, evacuation needed",
            "location": "Industrial District",
            "count": 50
        },
        {
            "desc": "Multi-vehicle pile-up on highway, multiple critical injuries, fuel leak",
            "location": "Highway I-95 Mile 42",
            "count": 15
        },
        {
            "desc": "Flash flood in residential area, families trapped on rooftops",
            "location": "Riverside Community",
            "count": 80
        },
        {
            "desc": "Fire in high-rise apartment, smoke on multiple floors, elderly residents",
            "location": "Downtown Tower Block",
            "count": 120
        }
    ]

    if random.random() < 0.4:
        scenario = random.choice(realistic_scenarios)

        # Full MeTTa analysis
        metta_analysis = analyze_with_metta(scenario["desc"])

        ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        ctx.logger.info(f"🚨 EMERGENCY DETECTED")
        ctx.logger.info(f"📝 {scenario['desc']}")
        ctx.logger.info(f"📍 Location: {scenario['location']}")
        ctx.logger.info(f"👥 Affected: {scenario['count']} people")

        ctx.logger.info(f"\n🧠 MeTTa Semantic Analysis:")
        ctx.logger.info(f"   Type Inference: {metta_analysis['inferred_type']}")
        ctx.logger.info(f"   Severity Score: {metta_analysis['severity_score']:.1f}/10")
        ctx.logger.info(f"   Confidence: {metta_analysis['confidence']:.1%}")
        ctx.logger.info(f"   Resources Required: {', '.join(metta_analysis['required_resources'])}")

        if metta_analysis['escalation_risk']:
            ctx.logger.info(f"   ⚠️ Escalation Risks: {', '.join(metta_analysis['escalation_risk'])}")

        emergency = EmergencyAlert(
            alert_id=f"EM{int(datetime.now().timestamp())}",
            timestamp=datetime.now().isoformat(),
            location={
                "lat": 40.7128 + random.uniform(-0.05, 0.05),
                "lng": -74.0060 + random.uniform(-0.05, 0.05)
            },
            emergency_type=metta_analysis['inferred_type'],
            severity="CRITICAL" if metta_analysis['severity_score'] > 7 else "HIGH",
            description=scenario["desc"],
            affected_count=scenario["count"]
        )

        active_emergencies[emergency.alert_id] = emergency

        # Smart dispatch
        ctx.logger.info(f"\n🚀 Dispatching Response Teams:")

        if "medical" in metta_analysis['required_resources'] or metta_analysis['inferred_type'] == "medical":
            await ctx.send(MEDICAL_AGENT, emergency)
            ctx.logger.info(f"   → Medical Response Team")

        if any(r in metta_analysis['required_resources'] for r in ["fire_equipment", "rescue_boats"]):
            await ctx.send(RESOURCE_AGENT, emergency)
            ctx.logger.info(f"   → Resource Allocation Unit")

        if scenario["count"] > 20 or metta_analysis['escalation_risk']:
            await ctx.send(SHELTER_AGENT, emergency)
            ctx.logger.info(f"   → Shelter Coordination")

        ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

@agent.on_message(model=EmergencyResponse)
async def handle_response_from_agents(ctx: Context, sender: str, msg: EmergencyResponse):
    agent_names = {
        MEDICAL_AGENT: "🏥 Medical",
        RESOURCE_AGENT: "📦 Resources",
        SHELTER_AGENT: "🏠 Shelter"
    }
    agent_name = agent_names.get(sender, "Unknown")
    ctx.logger.info(f"✅ {agent_name} confirmed: {msg.details}")

@agent.on_interval(period=60.0)
async def system_status(ctx: Context):
    if active_emergencies:
        critical = sum(1 for e in active_emergencies.values() if e.severity == "CRITICAL")
        ctx.logger.info(f"📊 System Status: {len(active_emergencies)} active | {critical} critical | {len(citizen_sessions)} citizens online")

# Include the chat protocol and publish the manifest to Agentverse
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()