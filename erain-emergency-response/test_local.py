#!/usr/bin/env python3
"""
Test ERAIN Emergency Response System Locally
No ASI:One needed - Direct agent communication test
"""

from uagents import Agent, Context, Model
from datetime import datetime
from typing import Dict
import asyncio

class EmergencyAlert(Model):
    alert_id: str
    timestamp: str
    location: Dict[str, float]
    emergency_type: str
    severity: str
    description: str
    affected_count: int

# Test agent to send emergency alerts
test_agent = Agent(
    name="test_emergency_sender",
    seed="test_emergency_seed_2024"
)

# Your actual deployed agent addresses from Agentverse
COORDINATOR = "agent1qf76r7qe6m2hc3qtm390q5xjuy38n66nnhfhh3dcwgsqn69sxeuqk0ejmhj"
MEDICAL = "agent1qgxzuzrukxv5sxp05vf4ma2l3u2u79t74nn5mkxw5fazqlyk3mkuulu7ykz"
RESOURCE = "agent1q2hlqe2jcmdea0c97k0h2tfk8fsunfxmrspuwv4uulh4nugwqk6astqd35r"
SHELTER = "agent1qwk8vrza032yre08rchhf74jfnmekswq8r20gvam22csz5av6x8ksjzntte"

@test_agent.on_event("startup")
async def send_test_emergency(ctx: Context):
    await asyncio.sleep(2)  # Wait for agent to initialize

    # Test Emergency 1: Fire
    fire_alert = EmergencyAlert(
        alert_id="TEST-001",
        timestamp=datetime.now().isoformat(),
        location={"lat": 40.7128, "lng": -74.0060},
        emergency_type="fire",
        severity="CRITICAL",
        description="🔥 TEST: Major fire at downtown building, smoke visible",
        affected_count=50
    )

    print("\n" + "="*50)
    print("📤 Sending FIRE emergency to Coordinator...")
    print(f"   Alert ID: {fire_alert.alert_id}")
    print(f"   Type: {fire_alert.emergency_type}")
    print(f"   Severity: {fire_alert.severity}")
    print(f"   Affected: {fire_alert.affected_count} people")
    print("="*50)

    # Send to coordinator
    await ctx.send(COORDINATOR, fire_alert)

    # Wait before next test
    await asyncio.sleep(5)

    # Test Emergency 2: Medical
    medical_alert = EmergencyAlert(
        alert_id="TEST-002",
        timestamp=datetime.now().isoformat(),
        location={"lat": 40.7589, "lng": -73.9851},
        emergency_type="medical",
        severity="HIGH",
        description="🚑 TEST: Multiple injuries from accident, urgent care needed",
        affected_count=15
    )

    print("\n" + "="*50)
    print("📤 Sending MEDICAL emergency to all agents...")
    print(f"   Alert ID: {medical_alert.alert_id}")
    print(f"   Type: {medical_alert.emergency_type}")
    print(f"   Severity: {medical_alert.severity}")
    print(f"   Affected: {medical_alert.affected_count} people")
    print("="*50)

    # Test direct communication with each agent
    await ctx.send(COORDINATOR, medical_alert)
    await ctx.send(MEDICAL, medical_alert)
    await ctx.send(RESOURCE, medical_alert)
    await ctx.send(SHELTER, medical_alert)

    print("\n✅ Test emergencies sent!")
    print("Check Agentverse logs for each agent to see responses!")

if __name__ == "__main__":
    print("\n🚨 ERAIN Emergency Response System - Local Test")
    print("=" * 50)
    print("This will send test emergencies to your deployed agents")
    print("Monitor the logs on Agentverse to see the coordination!")
    print("=" * 50)

    test_agent.run()