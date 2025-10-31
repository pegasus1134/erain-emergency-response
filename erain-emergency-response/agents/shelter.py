from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low
from datetime import datetime
from uuid import uuid4
from typing import Dict, List
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
    name="shelter_coordinator",
    seed="shelter_coordinator_seed_2024"
)

fund_agent_if_low(agent.wallet.address())

COORDINATOR = "agent1qf76r7qe6m2hc3qtm390q5xjuy38n66nnhfhh3dcwgsqn69sxeuqk0ejmhj"

# Shelter network
shelters = {
    "Central Community Center": {
        "capacity": 500,
        "current": 120,
        "address": "123 Main St, Downtown",
        "amenities": ["beds", "showers", "kitchen", "medical"],
        "pets_allowed": True,
        "distance": 2.3
    },
    "North High School": {
        "capacity": 800,
        "current": 200,
        "address": "456 Education Blvd",
        "amenities": ["cots", "restrooms", "cafeteria"],
        "pets_allowed": True,
        "distance": 4.1
    },
    "Convention Center": {
        "capacity": 1200,
        "current": 450,
        "address": "789 Convention Way",
        "amenities": ["beds", "showers", "medical", "childcare"],
        "pets_allowed": False,
        "distance": 3.5
    }
}

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

# Handle incoming chat messages
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

            # Respond with shelter availability
            response_text = "Shelter Availability:\n\n"
            for name, info in shelters.items():
                available = info["capacity"] - info["current"]
                occupancy = (info["current"] / info["capacity"]) * 100
                status = "🟢" if occupancy < 70 else "🟡" if occupancy < 90 else "🔴"
                response_text += f"{status} {name}: {available} spaces\n"

            response_message = create_text_chat(response_text)
            await ctx.send(sender, response_message)

        # Marks the end of a chat session
        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"Session ended with {sender}")
        # Catches anything unexpected
        else:
            ctx.logger.info(f"Received unexpected content type from {sender}")

# Handle acknowledgements for messages this agent has sent out
@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    ctx.logger.info(f"🏠 Shelter Coordination System Online")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"✅ Chat Protocol: ENABLED for ASI:One")
    ctx.logger.info(f"🏘️ Shelters Active: {len(shelters)}")

    total_capacity = sum(s["capacity"] for s in shelters.values())
    total_occupied = sum(s["current"] for s in shelters.values())
    ctx.logger.info(f"📊 Capacity: {total_occupied}/{total_capacity} ({(total_occupied/total_capacity)*100:.1f}%)")
    ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

@agent.on_message(model=EmergencyAlert)
async def handle_emergency_alert(ctx: Context, sender: str, msg: EmergencyAlert):
    ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    ctx.logger.info(f"🏠 SHELTER REQUEST RECEIVED")
    ctx.logger.info(f"📝 {msg.description}")
    ctx.logger.info(f"🆔 Alert: {msg.alert_id}")
    ctx.logger.info(f"👥 People needing shelter: {msg.affected_count}")

    # Find best shelter (most space and closest)
    best_shelter = None
    best_score = -1

    for name, info in shelters.items():
        available = info["capacity"] - info["current"]
        if available >= msg.affected_count:
            # Score based on space and distance
            score = available - (info["distance"] * 10)
            if score > best_score:
                best_score = score
                best_shelter = (name, info)

    if best_shelter:
        shelter_name = best_shelter[0]
        shelter_info = best_shelter[1]

        ctx.logger.info(f"\n🏘️ Shelter Assignment:")
        ctx.logger.info(f"   Selected: {shelter_name}")
        ctx.logger.info(f"   Address: {shelter_info['address']}")
        ctx.logger.info(f"   Available Space: {shelter_info['capacity'] - shelter_info['current']}")
        ctx.logger.info(f"   Distance: {shelter_info['distance']} km")
        ctx.logger.info(f"   Amenities: {', '.join(shelter_info['amenities'][:3])}")

        # Update occupancy
        shelters[shelter_name]["current"] = min(
            shelter_info["capacity"],
            shelter_info["current"] + msg.affected_count
        )

        details = f"{shelter_name} assigned | {msg.affected_count} spaces | {shelter_info['address']}"
    else:
        ctx.logger.info(f"   ⚠️ No suitable shelter with enough space")
        details = "All shelters at capacity - activating overflow protocol"

    # Send response to coordinator
    response = EmergencyResponse(
        alert_id=msg.alert_id,
        status="Shelter assigned",
        dispatch_time=datetime.now().isoformat(),
        teams_assigned=msg.affected_count,
        details=details
    )

    await ctx.send(COORDINATOR, response)
    ctx.logger.info(f"✅ Assignment confirmed to Coordinator")
    ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

@agent.on_interval(period=60.0)
async def shelter_status_update(ctx: Context):
    total_capacity = sum(s["capacity"] for s in shelters.values())
    total_occupied = sum(s["current"] for s in shelters.values())
    utilization = (total_occupied / total_capacity) * 100

    if utilization > 80:
        ctx.logger.info(f"⚠️ SHELTER ALERT: {utilization:.1f}% capacity utilized")

        for name, info in shelters.items():
            occupancy = (info["current"] / info["capacity"]) * 100
            if occupancy > 95:
                ctx.logger.info(f"   🔴 {name}: {occupancy:.1f}% full")

# Include the chat protocol and publish the manifest to Agentverse
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()