from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low
from datetime import datetime
from uuid import uuid4
from typing import Dict, List
import random
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
    name="medical_response",
    seed="medical_response_seed_2024"
)

fund_agent_if_low(agent.wallet.address())

COORDINATOR = "agent1qf76r7qe6m2hc3qtm390q5xjuy38n66nnhfhh3dcwgsqn69sxeuqk0ejmhj"

# Hospital network
hospitals = {
    "Central Medical Center": {
        "capacity": 500,
        "current": 342,
        "icu": 12,
        "distance": 2.5
    },
    "St. Mary's Hospital": {
        "capacity": 300,
        "current": 189,
        "icu": 8,
        "distance": 4.0
    },
    "Emergency Care Unit": {
        "capacity": 150,
        "current": 98,
        "icu": 5,
        "distance": 1.8
    }
}

ambulances = {"available": 15, "dispatched": 0}

# Initialize the chat protocol with the standard chat spec - EXACTLY AS SHOWN
chat_proto = Protocol(spec=chat_protocol_spec)

# Utility function to wrap plain text into a ChatMessage - EXACTLY AS SHOWN
def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent())
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=content,
    )

# Handle incoming chat messages - EXACTLY AS SHOWN IN DOCS
@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"Received message from {sender}")

    # Always send back an acknowledgement when a message is received
    await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id))

    # Process each content item inside the chat message
    for item in msg.content:
        # Marks the start of a chat session
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Session started with {sender}")

        # Handles plain text messages (from another agent or ASI:One)
        elif isinstance(item, TextContent):
            ctx.logger.info(f"Text message from {sender}: {item.text}")

            # Respond with medical status
            response_text = (
                f"Medical Response System Status:\n"
                f"Ambulances Available: {ambulances['available']}/15\n"
                f"Hospitals Connected: {len(hospitals)}\n"
                f"Ready for emergencies"
            )
            response_message = create_text_chat(response_text)
            await ctx.send(sender, response_message)

        # Marks the end of a chat session
        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"Session ended with {sender}")
        # Catches anything unexpected
        else:
            ctx.logger.info(f"Received unexpected content type from {sender}")

# Handle acknowledgements for messages this agent has sent out - EXACTLY AS SHOWN
@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    ctx.logger.info(f"🏥 Medical Response Agent Online")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"✅ Chat Protocol: ENABLED for ASI:One")
    ctx.logger.info(f"🚑 Ambulances Available: {ambulances['available']}")
    ctx.logger.info(f"🏥 Hospitals Connected: {len(hospitals)}")
    ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

@agent.on_message(model=EmergencyAlert)
async def handle_emergency_alert(ctx: Context, sender: str, msg: EmergencyAlert):
    ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    ctx.logger.info(f"🚨 MEDICAL EMERGENCY RECEIVED")
    ctx.logger.info(f"📝 {msg.description}")
    ctx.logger.info(f"📍 Alert ID: {msg.alert_id}")
    ctx.logger.info(f"⚠️ Severity: {msg.severity}")
    ctx.logger.info(f"👥 Affected: {msg.affected_count}")

    # Find best hospital
    best_hosp = min(hospitals.items(), key=lambda x: x[1]["distance"])
    hosp_name = best_hosp[0]
    hosp_info = best_hosp[1]

    # Calculate ambulances needed
    if msg.severity == "CRITICAL":
        needed = min(3, ambulances["available"])
    elif msg.severity == "HIGH":
        needed = min(2, ambulances["available"])
    else:
        needed = min(1, ambulances["available"])

    ambulances["available"] -= needed
    ambulances["dispatched"] += needed

    ctx.logger.info(f"\n🏥 Hospital Selection:")
    ctx.logger.info(f"   Selected: {hosp_name}")
    ctx.logger.info(f"   Available Beds: {hosp_info['capacity'] - hosp_info['current']}")
    ctx.logger.info(f"   ICU Available: {hosp_info['icu']}")
    ctx.logger.info(f"   Distance: {hosp_info['distance']} km")

    ctx.logger.info(f"\n🚑 Ambulance Dispatch:")
    ctx.logger.info(f"   Units Dispatched: {needed}")
    ctx.logger.info(f"   ETA: {int(hosp_info['distance'] * 3)} minutes")

    # Send response to coordinator
    response = EmergencyResponse(
        alert_id=msg.alert_id,
        status="Medical teams dispatched",
        dispatch_time=datetime.now().isoformat(),
        teams_assigned=needed,
        details=f"{needed} ambulances to {hosp_name} | ETA: {int(hosp_info['distance'] * 3)}min"
    )

    await ctx.send(COORDINATOR, response)
    ctx.logger.info(f"✅ Response sent to Coordinator")
    ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

@agent.on_interval(period=30.0)
async def update_status(ctx: Context):
    if ambulances["dispatched"] > 0 and random.random() < 0.3:
        ambulances["available"] += 1
        ambulances["dispatched"] -= 1
        ctx.logger.info(f"🚑 Ambulance returned to service")

# Include the chat protocol and publish the manifest to Agentverse - EXACTLY AS SHOWN
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()