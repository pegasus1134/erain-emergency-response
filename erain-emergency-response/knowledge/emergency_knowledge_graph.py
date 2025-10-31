"""
MeTTa Knowledge Graph Integration for Emergency Response
Provides semantic reasoning and decision support using SingularityNET's MeTTa
"""

from hyperon import MeTTa, GroundedAtom, ExpressionAtom, SymbolAtom, E, S
from typing import Dict, List, Tuple, Optional
import json

class EmergencyKnowledgeGraph:
    """
    Knowledge graph for emergency response using MeTTa
    Enables semantic reasoning about resources, locations, and emergency types
    """

    def __init__(self):
        self.metta = MeTTa()
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """Initialize the emergency response knowledge base"""

        # Define emergency type hierarchy
        self.metta.add_parse("""
            ; Emergency type ontology
            (: emergency-type Type)
            (: medical emergency-type)
            (: fire emergency-type)
            (: flood emergency-type)
            (: earthquake emergency-type)
            (: chemical-spill emergency-type)

            ; Severity levels
            (: severity-level Type)
            (: critical severity-level)
            (: high severity-level)
            (: medium severity-level)
            (: low severity-level)

            ; Resource types
            (: resource-type Type)
            (: ambulance resource-type)
            (: fire-truck resource-type)
            (: rescue-boat resource-type)
            (: helicopter resource-type)
            (: medical-supplies resource-type)
            (: emergency-team resource-type)

            ; Define relationships
            (: requires (-> emergency-type resource-type Bool))
            (: priority-for (-> severity-level resource-type Number))
            (: compatible-with (-> resource-type emergency-type Bool))
            (: escalates-to (-> emergency-type emergency-type Bool))

            ; Emergency-Resource mappings
            (= (requires medical ambulance) True)
            (= (requires medical medical-supplies) True)
            (= (requires medical emergency-team) True)
            (= (requires fire fire-truck) True)
            (= (requires fire emergency-team) True)
            (= (requires flood rescue-boat) True)
            (= (requires flood emergency-team) True)
            (= (requires earthquake medical-supplies) True)
            (= (requires earthquake emergency-team) True)
            (= (requires chemical-spill hazmat-team) True)

            ; Priority scoring
            (= (priority-for critical ambulance) 10)
            (= (priority-for critical helicopter) 10)
            (= (priority-for critical emergency-team) 9)
            (= (priority-for high ambulance) 8)
            (= (priority-for high emergency-team) 7)
            (= (priority-for medium emergency-team) 5)
            (= (priority-for low emergency-team) 3)

            ; Escalation patterns
            (= (escalates-to fire chemical-spill) True)
            (= (escalates-to flood medical) True)
            (= (escalates-to earthquake fire) True)
            (= (escalates-to earthquake medical) True)

            ; Location types
            (: location-type Type)
            (: hospital location-type)
            (: shelter location-type)
            (: depot location-type)
            (: danger-zone location-type)

            ; Distance calculation function
            (: calculate-distance (-> Number Number Number Number Number))
            (= (calculate-distance $lat1 $lng1 $lat2 $lng2)
               (sqrt (+ (pow (- $lat1 $lat2) 2)
                       (pow (- $lng1 $lng2) 2))))

            ; Resource allocation rules
            (: optimal-resource (-> emergency-type severity-level resource-type))
            (= (optimal-resource medical critical) ambulance)
            (= (optimal-resource medical high) ambulance)
            (= (optimal-resource fire critical) fire-truck)
            (= (optimal-resource flood critical) rescue-boat)

            ; Response time estimation
            (: estimate-response-time (-> Number severity-level Number))
            (= (estimate-response-time $distance critical) (* $distance 1.5))
            (= (estimate-response-time $distance high) (* $distance 2.0))
            (= (estimate-response-time $distance medium) (* $distance 2.5))
            (= (estimate-response-time $distance low) (* $distance 3.0))

            ; Triage rules
            (: triage-score (-> emergency-type severity-level Number Number))
            (= (triage-score medical critical $affected)
               (* $affected 10))
            (= (triage-score medical high $affected)
               (* $affected 7))
            (= (triage-score fire critical $affected)
               (* $affected 9))
            (= (triage-score flood high $affected)
               (* $affected 6))
        """)

        # Add specific knowledge about resources and locations
        self.metta.add_parse("""
            ; Specific hospital capabilities
            (: has-capability (-> String String Bool))
            (= (has-capability "Central Medical Center" "trauma-center") True)
            (= (has-capability "Central Medical Center" "burn-unit") True)
            (= (has-capability "St. Mary's Hospital" "trauma-center") True)
            (= (has-capability "Emergency Care Unit" "basic-emergency") True)

            ; Resource availability patterns
            (: peak-demand-time (-> resource-type Number))
            (= (peak-demand-time ambulance) 18) ; 6 PM
            (= (peak-demand-time fire-truck) 14) ; 2 PM
            (= (peak-demand-time emergency-team) 12) ; Noon

            ; Collaboration rules between agents
            (: should-collaborate (-> emergency-type emergency-type Bool))
            (= (should-collaborate medical fire) True)
            (= (should-collaborate flood medical) True)
            (= (should-collaborate earthquake medical) True)
            (= (should-collaborate chemical-spill medical) True)

            ; Resource sharing rules
            (: can-share-resource (-> String String resource-type Bool))
            (= (can-share-resource "depot_north" "depot_central" medical-supplies) True)
            (= (can-share-resource "depot_central" "depot_south" emergency-team) True)
        """)

    def query_required_resources(self, emergency_type: str) -> List[str]:
        """Query which resources are required for an emergency type"""
        result = self.metta.run(f"""
            (match &self (requires {emergency_type} $resource)
                   $resource)
        """)
        return [str(r) for r in result[0] if r]

    def calculate_priority_score(self, emergency_type: str, severity: str, affected_count: int) -> float:
        """Calculate priority score for an emergency"""
        result = self.metta.run(f"""
            (triage-score {emergency_type} {severity} {affected_count})
        """)
        try:
            return float(result[0][0]) if result[0] else 0.0
        except:
            return 0.0

    def find_optimal_resource(self, emergency_type: str, severity: str) -> Optional[str]:
        """Find the optimal resource for an emergency"""
        result = self.metta.run(f"""
            (optimal-resource {emergency_type} {severity})
        """)
        return str(result[0][0]) if result[0] else None

    def estimate_response_time(self, distance: float, severity: str) -> float:
        """Estimate response time based on distance and severity"""
        result = self.metta.run(f"""
            (estimate-response-time {distance} {severity})
        """)
        try:
            return float(result[0][0]) if result[0] else distance * 2
        except:
            return distance * 2

    def check_escalation_risk(self, emergency_type: str) -> List[str]:
        """Check if an emergency might escalate to other types"""
        result = self.metta.run(f"""
            (match &self (escalates-to {emergency_type} $escalated)
                   $escalated)
        """)
        return [str(r) for r in result[0] if r]

    def should_agents_collaborate(self, emergency1: str, emergency2: str) -> bool:
        """Determine if two emergency types should trigger agent collaboration"""
        result = self.metta.run(f"""
            (should-collaborate {emergency1} {emergency2})
        """)
        return bool(result[0][0]) if result[0] else False

    def get_hospital_capabilities(self, hospital_name: str) -> List[str]:
        """Get capabilities of a specific hospital"""
        capabilities = []
        for capability in ["trauma-center", "burn-unit", "cardiac-unit", "pediatric-icu"]:
            result = self.metta.run(f"""
                (has-capability "{hospital_name}" "{capability}")
            """)
            if result[0] and result[0][0]:
                capabilities.append(capability)
        return capabilities

    def infer_resource_needs(self, emergency_description: str) -> Dict[str, any]:
        """
        Use semantic reasoning to infer resource needs from emergency description
        """
        # Keywords analysis for emergency type inference
        keywords_emergency_map = {
            "injured": "medical",
            "bleeding": "medical",
            "heart": "medical",
            "fire": "fire",
            "burning": "fire",
            "smoke": "fire",
            "flood": "flood",
            "water": "flood",
            "drowning": "flood",
            "earthquake": "earthquake",
            "chemical": "chemical-spill",
            "toxic": "chemical-spill"
        }

        keywords_severity_map = {
            "critical": "critical",
            "dying": "critical",
            "severe": "high",
            "urgent": "high",
            "minor": "low",
            "stable": "medium"
        }

        desc_lower = emergency_description.lower()

        # Infer emergency type
        emergency_type = "medical"  # default
        for keyword, etype in keywords_emergency_map.items():
            if keyword in desc_lower:
                emergency_type = etype
                break

        # Infer severity
        severity = "medium"  # default
        for keyword, sev in keywords_severity_map.items():
            if keyword in desc_lower:
                severity = sev
                break

        # Get required resources
        resources = self.query_required_resources(emergency_type)

        # Check escalation risks
        escalation_risks = self.check_escalation_risk(emergency_type)

        # Get optimal resource
        optimal = self.find_optimal_resource(emergency_type, severity)

        return {
            "inferred_type": emergency_type,
            "inferred_severity": severity,
            "required_resources": resources,
            "optimal_resource": optimal,
            "escalation_risks": escalation_risks,
            "priority_score": self.calculate_priority_score(emergency_type, severity, 1)
        }

    def optimize_multi_agent_response(self, emergencies: List[Dict]) -> List[Dict]:
        """
        Optimize response across multiple emergencies using knowledge graph reasoning
        """
        optimized_responses = []

        for emergency in emergencies:
            inference = self.infer_resource_needs(emergency.get("description", ""))

            # Check for collaboration opportunities
            collaborations = []
            for other in emergencies:
                if other != emergency:
                    other_inference = self.infer_resource_needs(other.get("description", ""))
                    if self.should_agents_collaborate(
                        inference["inferred_type"],
                        other_inference["inferred_type"]
                    ):
                        collaborations.append(other.get("id"))

            response = {
                "emergency_id": emergency.get("id"),
                "priority": inference["priority_score"],
                "assigned_resources": inference["required_resources"],
                "optimal_resource": inference["optimal_resource"],
                "collaborate_with": collaborations,
                "escalation_watch": inference["escalation_risks"]
            }

            optimized_responses.append(response)

        # Sort by priority
        optimized_responses.sort(key=lambda x: x["priority"], reverse=True)

        return optimized_responses


# Integration with uAgents
class MeTTaReasoningAgent:
    """
    Wrapper to integrate MeTTa reasoning with uAgents framework
    """

    def __init__(self):
        self.knowledge_graph = EmergencyKnowledgeGraph()

    async def process_emergency(self, emergency_data: Dict) -> Dict:
        """Process emergency using knowledge graph reasoning"""
        inference = self.knowledge_graph.infer_resource_needs(
            emergency_data.get("description", "")
        )

        # Enhance with location-based reasoning if available
        if "location" in emergency_data:
            # Estimate response times for different severities
            distance = emergency_data.get("distance_to_resources", 5.0)
            inference["estimated_response_time"] = \
                self.knowledge_graph.estimate_response_time(distance, inference["inferred_severity"])

        return inference

    async def coordinate_multi_agent_response(self, emergencies: List[Dict]) -> List[Dict]:
        """Coordinate multiple agents using knowledge graph"""
        return self.knowledge_graph.optimize_multi_agent_response(emergencies)

    def get_resource_requirements(self, emergency_type: str) -> List[str]:
        """Get resource requirements for emergency type"""
        return self.knowledge_graph.query_required_resources(emergency_type)

    def check_hospital_suitability(self, hospital: str, emergency_type: str) -> bool:
        """Check if hospital is suitable for emergency type"""
        capabilities = self.knowledge_graph.get_hospital_capabilities(hospital)

        if emergency_type == "medical":
            return "trauma-center" in capabilities
        elif emergency_type == "fire":
            return "burn-unit" in capabilities
        else:
            return len(capabilities) > 0


# Integration point for agents
def get_metta_analysis(description: str) -> Dict:
    """Public API for agents to use MeTTa reasoning"""
    kg = EmergencyKnowledgeGraph()
    return kg.infer_resource_needs(description)

# Example usage and testing
if __name__ == "__main__":
    # Initialize knowledge graph
    kg = EmergencyKnowledgeGraph()

    # Test inference
    test_emergency = "Multiple people injured in building collapse, some critical with severe bleeding"
    result = kg.infer_resource_needs(test_emergency)
    print(f"Emergency Analysis: {json.dumps(result, indent=2)}")

    # Test multi-agent optimization
    emergencies = [
        {"id": "1", "description": "Major fire in downtown, people trapped"},
        {"id": "2", "description": "Flooding in residential area, families need evacuation"},
        {"id": "3", "description": "Critical medical emergency, cardiac arrest"}
    ]

    optimized = kg.optimize_multi_agent_response(emergencies)
    print(f"\nOptimized Response Plan: {json.dumps(optimized, indent=2)}")

    print("\n✅ MeTTa Knowledge Graph Ready for Agent Integration")