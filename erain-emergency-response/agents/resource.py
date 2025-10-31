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
    name="resource_allocation",
    seed="resource_allocation_seed_2024"
)

fund_agent_if_low(agent.wallet.address())

COORDINATOR = "agent1qfvx3gqgpngs7n8n5gjqh3ey0z9fee4wn2nz6r9g0glrqeu5stark6kpqzx"

# Depots
depots = {
    "North Depot": {
        "medical_supplies": 500,
        "emergency_teams": 5,
        "fire_equipment": 20,
        "rescue_boats": 3,
        "distance": 3.0
    },
    "Central Depot": {
        "medical_supplies": 1000,
        "emergency_teams": 8,
        "fire_equipment": 30,
        "rescue_boats": 5,
        "distance": 1.5
    },
    "South Depot": {
        "medical_supplies": 400,
        "emergency_teams": 4,
        "fire_equipment": 15,
        "rescue_boats": 2,
        "distance": 4.5
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

            # Respond with resource status
            total_resources = sum(
                sum(v for k, v in depot.items() if isinstance(v, int) and k != "distance")
                for depot in depots.values()
            )
            response_text = (
                f"Resource Allocation System Status:\n"
                f"Depots Active: {len(depots)}\n"
                f"Total Resources: {total_resources} units\n"
                f"Ready for allocation"
            )
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
    ctx.logger.info(f"📦 Resource Allocation System Online")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"✅ Chat Protocol: ENABLED for ASI:One")
    ctx.logger.info(f"🏭 Depots Active: {len(depots)}")

    total_resources = sum(
        sum(v for k, v in depot.items() if isinstance(v, int) and k != "distance")
        for depot in depots.values()
    )
    ctx.logger.info(f"📊 Total Resources: {total_resources} units")
    ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

@agent.on_message(model=EmergencyAlert)
async def handle_emergency_alert(ctx: Context, sender: str, msg: EmergencyAlert):
    ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    ctx.logger.info(f"📦 RESOURCE REQUEST RECEIVED")
    ctx.logger.info(f"📝 {msg.description}")
    ctx.logger.info(f"🆔 Alert: {msg.alert_id}")
    ctx.logger.info(f"🔥 Type: {msg.emergency_type}")
    ctx.logger.info(f"👥 Affected: {msg.affected_count}")

    # Find best depot (closest)
    best_depot = min(depots.items(), key=lambda x: x[1]["distance"])
    depot_name = best_depot[0]
    depot_info = best_depot[1]

    # Determine resource needs
    if msg.emergency_type == "fire":
        resource = "fire_equipment"
        quantity = 5 if msg.severity == "CRITICAL" else 2
    elif msg.emergency_type == "flood":
        resource = "rescue_boats"
        quantity = 2 if msg.severity == "HIGH" else 1
    elif msg.emergency_type == "medical":
        resource = "medical_supplies"
        quantity = 50 if msg.severity == "CRITICAL" else 20
    else:
        resource = "emergency_teams"
        quantity = 3 if msg.severity == "HIGH" else 1

    ctx.logger.info(f"\n🎯 Resource Optimization:")
    ctx.logger.info(f"   Resource Type: {resource}")
    ctx.logger.info(f"   Quantity Needed: {quantity}")
    ctx.logger.info(f"   Selected Depot: {depot_name}")
    ctx.logger.info(f"   Distance: {depot_info['distance']} km")

    # Allocate if available
    if resource in depot_info and depot_info[resource] >= quantity:
        depots[depot_name][resource] -= quantity
        ctx.logger.info(f"   ✅ Allocated {quantity} {resource}")
        details = f"Allocated {quantity} {resource} from {depot_name} | ETA: {int(depot_info['distance'] * 10)}min"
        teams = quantity if resource == "emergency_teams" else 0
    else:
        ctx.logger.info(f"   ⚠️ Insufficient {resource}")
        details = "Partial allocation due to shortage"
        teams = 0

    # Send response to coordinator
    response = EmergencyResponse(
        alert_id=msg.alert_id,
        status="Resources allocated",
        dispatch_time=datetime.now().isoformat(),
        teams_assigned=teams,
        details=details
    )

    await ctx.send(COORDINATOR, response)
    ctx.logger.info(f"✅ Allocation confirmed to Coordinator")
    ctx.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

@agent.on_interval(period=45.0)
async def optimize_inventory(ctx: Context):
    # Check for critical shortages
    for resource in ["emergency_teams", "medical_supplies"]:
        total = sum(depot.get(resource, 0) for depot in depots.values())
        if total < 10:
            ctx.logger.info(f"⚠️ CRITICAL SHORTAGE: {resource} - Only {total} units remaining")

# Include the chat protocol and publish the manifest to Agentverse
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()