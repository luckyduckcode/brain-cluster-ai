"""
Frontal Lobe: Executive function and meta-cognition system.

The Frontal Lobe serves as the executive center of the Digital Cortex, responsible for
high-level reasoning, planning, meta-cognition, and final decision-making. It synthesizes
information from all other brain regions to make informed, strategic decisions.
"""

import sys
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..utils.message import Message
from ..utils.llm_neuron import LLMNeuron
from ..cortex_regions.meta_cognition import MetaCognitionLayer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExecutiveDecision:
    """Result of executive decision-making."""
    decision: str
    confidence: float
    reasoning: str
    action_plan: List[str]
    risk_assessment: str
    alternatives_considered: List[str]
    meta_cognition: str  # Thinking about the thinking process


class FrontalLobe:
    """
    Executive function and meta-cognition system.

    The Frontal Lobe acts as the CEO of the brain, synthesizing information from all
    other regions to make strategic decisions, plan actions, and perform meta-cognition.
    """

    def __init__(self, model: str = "llama3.2:1b", temperature: float = 0.3):
        """
        Initialize the Frontal Lobe.

        Args:
            model: LLM model to use for executive reasoning
            temperature: Temperature for decision-making (lower = more consistent)
        """
        self.model = model
        self.temperature = temperature
        self.neuron = LLMNeuron(
            name="Frontal_Lobe_Executive",
            model=model,
            temperature=temperature
        )
        
        self.meta_layer = MetaCognitionLayer()

        # System prompt for executive function
        self.system_prompt = """
        You are the Frontal Lobe, the executive center of a digital brain. Your role is to:

        1. SYNTHESIZE information from all brain regions (Sensorium, Amygdala, Neurons, Memory)
        2. PERFORM META-COGNITION (think about your own thinking and decision processes)
        3. MAKE STRATEGIC DECISIONS based on consensus, threats, and context
        4. PLAN ACTIONS with risk assessment and alternatives
        5. PROVIDE CLEAR REASONING for all decisions

        Consider:
        - Threat levels and urgency from Amygdala
        - Sensory data quality and context
        - Consensus strength and alternative viewpoints
        - Historical patterns from Memory Palace
        - Risk-benefit analysis of different options

        Always provide structured output with:
        - Final Decision
        - Confidence Level (0.0-1.0)
        - Detailed Reasoning
        - Action Plan (step-by-step)
        - Risk Assessment
        - Alternatives Considered
        - Meta-cognition (reflection on decision process)
        """

        logger.info(f"Frontal Lobe initialized with {model} (executive decision-making)")

    def make_executive_decision(self,
                               consensus_message: Message,
                               amygdala_assessment: Optional[Dict[str, Any]] = None,
                               sensory_context: Optional[Dict[str, Any]] = None,
                               memory_context: Optional[List[Dict[str, Any]]] = None,
                               available_actions: Optional[List[str]] = None) -> ExecutiveDecision:
        """
        Make an executive decision by synthesizing all available information.

        Args:
            consensus_message: The winning consensus from Colosseum
            amygdala_assessment: Threat assessment from Amygdala
            sensory_context: Sensory information from Sensorium
            memory_context: Relevant memories from Memory Palace
            available_actions: List of possible actions to consider

        Returns:
            ExecutiveDecision with comprehensive analysis and plan
        """
        # Monitor consensus state
        cognitive_state = self.meta_layer.monitor_consensus(consensus_message.metadata)
        
        # Build comprehensive context
        context = self._build_decision_context(
            consensus_message, amygdala_assessment, sensory_context,
            memory_context, available_actions
        )
        
        # Add cognitive state to context
        context["cognitive_state"] = cognitive_state

        # Create executive reasoning prompt
        prompt = self._create_executive_prompt(context)

        # Get executive decision from LLM
        response = self.neuron.process(prompt)

        # Parse the structured response
        decision = self._parse_executive_response(response.content)

        logger.info(f"Frontal Lobe executive decision made: {decision.decision[:50]}...")
        return decision

    def perform_meta_cognition(self, recent_decisions: List[ExecutiveDecision],
                              system_performance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform meta-cognition: analyze the system's own thinking and performance.

        Args:
            recent_decisions: Recent executive decisions
            system_performance: Overall system performance metrics

        Returns:
            Meta-cognitive analysis and recommendations
        """
        if not recent_decisions:
            return {"analysis": "No recent decisions to analyze", "recommendations": []}

        # Analyze decision patterns
        decision_patterns = self._analyze_decision_patterns(recent_decisions)

        # Assess system performance
        performance_analysis = self._assess_system_performance(system_performance)
        
        # Get real-time meta-cognitive status
        meta_status = self.meta_layer.get_status()

        # Generate meta-cognitive insights
        prompt = f"""
        Perform meta-cognition on the following system analysis:

        REAL-TIME COGNITIVE STATE:
        {meta_status}

        DECISION PATTERNS:
        {decision_patterns}

        SYSTEM PERFORMANCE:
        {performance_analysis}

        Provide insights about:
        1. Decision-making effectiveness
        2. Risk assessment accuracy
        3. Learning and adaptation patterns
        4. Potential biases or blind spots
        5. Recommendations for improvement

        Be reflective and analytical.
        """

        response = self.neuron.process(prompt)

        return {
            "decision_patterns": decision_patterns,
            "performance_analysis": performance_analysis,
            "meta_cognitive_insights": response.content,
            "recommendations": self._extract_recommendations(response.content)
        }

    def plan_action_sequence(self, goal: str, constraints: Dict[str, Any],
                           available_resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan a sequence of actions to achieve a goal.

        Args:
            goal: The goal to achieve
            constraints: Constraints and limitations
            available_resources: Available resources and capabilities

        Returns:
            Action plan with steps, risks, and contingencies
        """
        prompt = f"""
        Create a detailed action plan for the goal: {goal}

        CONSTRAINTS:
        {constraints}

        AVAILABLE RESOURCES:
        {available_resources}

        Provide:
        1. Step-by-step action plan
        2. Risk assessment for each step
        3. Contingency plans for potential failures
        4. Success criteria
        5. Timeline estimates
        6. Resource requirements

        Be strategic, realistic, and thorough.
        """

        response = self.neuron.process(prompt)

        return {
            "goal": goal,
            "action_plan": self._parse_action_plan(response.content),
            "raw_reasoning": response.content
        }

    def _build_decision_context(self, consensus: Message, amygdala: Optional[Dict],
                               sensory: Optional[Dict], memory: Optional[List],
                               actions: Optional[List]) -> Dict[str, Any]:
        """Build comprehensive context for decision-making."""
        context = {
            "consensus": {
                "content": consensus.content,
                "source": consensus.source,
                "confidence": consensus.confidence,
                "metadata": consensus.metadata
            }
        }

        if amygdala:
            context["amygdala"] = amygdala

        if sensory:
            context["sensory"] = sensory

        if memory:
            # Include full memory details for comprehensive context
            context["memory"] = {
                "count": len(memory),
                "memories": memory,  # Include full memory list
                "recent_decisions": [m.get("content", "") for m in memory[:3]],
                "patterns": self._extract_memory_patterns(memory)
            }

        if actions:
            context["available_actions"] = actions

        return context

    def _create_executive_prompt(self, context: Dict[str, Any]) -> str:
        """Create a structured prompt for executive decision-making."""
        prompt = f"""
        {self.system_prompt}

        CURRENT SITUATION ANALYSIS:

        CONSENSUS DECISION:
        - Content: {context['consensus']['content']}
        - Source: {context['consensus']['source']}
        - Confidence: {context['consensus']['confidence']:.2f}

        AMYGDALA ASSESSMENT:
        {self._format_amygdala_context(context.get('amygdala'))}

        SENSORY CONTEXT:
        {self._format_sensory_context(context.get('sensory'))}

        MEMORY CONTEXT:
        {self._format_memory_context(context.get('memory'))}

        AVAILABLE ACTIONS:
        {self._format_actions(context.get('available_actions'))}

        Based on all this information, make an executive decision following the required structure.
        """

        return prompt

    def _parse_executive_response(self, response: str) -> ExecutiveDecision:
        """Parse the structured executive response."""
        # Simple parsing - in a more sophisticated implementation,
        # this could use more advanced NLP techniques

        lines = response.split('\n')
        decision = "Unable to parse decision"
        confidence = 0.5
        reasoning = response
        action_plan = []
        risk_assessment = "Unknown"
        alternatives = []
        meta_cognition = "Decision process analysis not available"

        # Try to extract structured information
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections
            if "FINAL DECISION" in line.upper() or "DECISION:" in line.upper():
                current_section = "decision"
                # Extract decision if it's on the same line
                if ":" in line:
                    decision = line.split(":", 1)[1].strip()
                continue
            elif "CONFIDENCE" in line.upper():
                current_section = "confidence"
                # Extract confidence if it's on the same line
                if ":" in line:
                    try:
                        confidence_str = line.split(":", 1)[1].strip()
                        confidence = float(confidence_str.split()[0])
                    except:
                        pass
                continue
            elif "REASONING" in line.upper():
                current_section = "reasoning"
                # Extract reasoning if it's on the same line
                if ":" in line:
                    reasoning = line.split(":", 1)[1].strip()
                continue
            elif "ACTION PLAN" in line.upper():
                current_section = "action_plan"
                continue
            elif "RISK ASSESSMENT" in line.upper():
                current_section = "risk"
                # Extract risk if it's on the same line
                if ":" in line:
                    risk_assessment = line.split(":", 1)[1].strip()
                continue
            elif "ALTERNATIVES" in line.upper():
                current_section = "alternatives"
                continue
            elif "META-COGNITION" in line.upper():
                current_section = "meta"
                # Extract meta-cognition if it's on the same line
                if ":" in line:
                    meta_cognition = line.split(":", 1)[1].strip()
                continue

            # Extract content based on section
            if current_section == "decision" and decision == "Unable to parse decision":
                decision = line
            elif current_section == "confidence" and "confidence" not in line.lower():
                try:
                    confidence = float(line.split()[0])
                except:
                    pass
            elif current_section == "action_plan" and line.startswith(("-", "*", "1.")):
                action_plan.append(line.lstrip("-*123456789. "))
            elif current_section == "risk":
                risk_assessment = line
            elif current_section == "alternatives" and line.startswith(("-", "*", "1.")):
                alternatives.append(line.lstrip("-*123456789. "))
            elif current_section == "meta":
                meta_cognition = line

        return ExecutiveDecision(
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            action_plan=action_plan,
            risk_assessment=risk_assessment,
            alternatives_considered=alternatives,
            meta_cognition=meta_cognition
        )

    def _format_amygdala_context(self, amygdala: Optional[Dict]) -> str:
        """Format amygdala assessment for prompt."""
        if not amygdala:
            return "- No amygdala assessment available"

        return f"""
        - Threat Level: {amygdala.get('threat_level', 0):.2f}
        - Urgency: {amygdala.get('urgency', 0):.2f}
        - Valence: {amygdala.get('valence', 0):.2f}
        - Triggers: {', '.join(amygdala.get('triggers', [])[:3])}
        - Reasoning: {amygdala.get('reasoning', 'N/A')}
        """

    def _format_sensory_context(self, sensory: Optional[Dict]) -> str:
        """Format sensory context for prompt."""
        if not sensory:
            return "- No sensory context available"

        return f"""
        - Type: {sensory.get('sensorium_type', 'unknown')}
        - Analysis: {sensory.get('text_analysis', {}).get('word_count', 0)} words
        - Context: {sensory.get('capture_context', 'general')}
        """

    def _format_memory_context(self, memory: Optional[Dict]) -> str:
        """Format memory context for prompt."""
        if not memory:
            return "- No memory context available"

        formatted = f"""
        - Memories available: {memory.get('count', 0)}
        - Recent decisions: {len(memory.get('recent_decisions', []))}
        - Patterns: {memory.get('patterns', 'None identified')}
        """

        # Include actual memory content for better context
        memories = memory.get('memories', [])
        if memories:
            formatted += "\n        RECENT MEMORY CONTENT:"
            for i, mem in enumerate(memories[:3]):  # Show top 3 memories
                content = mem.get('content', '')[:200]  # Truncate long content
                relevance = mem.get('relevance_score', 0)
                outcome = mem.get('outcome', {})
                formatted += f"\n        {i+1}. [{relevance:.2f}] {content}..."
                if outcome:
                    formatted += f"\n           Outcome: {outcome}"

        return formatted

    def _format_actions(self, actions: Optional[List]) -> str:
        """Format available actions for prompt."""
        if not actions:
            return "- No specific actions available (general decision-making)"

        return "\n".join(f"- {action}" for action in actions)

    def _analyze_decision_patterns(self, decisions: List[ExecutiveDecision]) -> str:
        """Analyze patterns in recent decisions."""
        if not decisions:
            return "No decisions to analyze"

        avg_confidence = sum(d.confidence for d in decisions) / len(decisions)
        high_risk_decisions = sum(1 for d in "high risk" in d.risk_assessment.lower() or "danger" in d.risk_assessment.lower())

        return f"""
        - Total decisions analyzed: {len(decisions)}
        - Average confidence: {avg_confidence:.2f}
        - High-risk decisions: {high_risk_decisions}
        - Most common decision type: {self._find_common_decision_type(decisions)}
        """

    def _assess_system_performance(self, performance: Dict[str, Any]) -> str:
        """Assess overall system performance."""
        return f"""
        - Consensus success rate: {performance.get('consensus_success_rate', 'Unknown')}
        - Average decision confidence: {performance.get('avg_decision_confidence', 'Unknown')}
        - Memory utilization: {performance.get('memory_utilization', 'Unknown')}
        - Learning effectiveness: {performance.get('learning_effectiveness', 'Unknown')}
        """

    def _extract_recommendations(self, meta_insights: str) -> List[str]:
        """Extract recommendations from meta-cognitive insights."""
        recommendations = []
        lines = meta_insights.split('\n')

        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['recommend', 'should', 'could', 'improve', 'suggest']):
                recommendations.append(line)

        return recommendations[:5]  # Limit to top 5

    def _extract_memory_patterns(self, memories: List[Dict]) -> str:
        """Extract patterns from memory data."""
        if not memories:
            return "No patterns available"

        # Simple pattern extraction - could be more sophisticated
        decision_types = []
        for memory in memories:
            content = memory.get('content', '').lower()
            if 'threat' in content or 'danger' in content:
                decision_types.append('threat_response')
            elif 'safe' in content or 'normal' in content:
                decision_types.append('routine')
            else:
                decision_types.append('analysis')

        from collections import Counter
        most_common = Counter(decision_types).most_common(1)
        return f"Most common decision type: {most_common[0][0] if most_common else 'none'}"

    def _find_common_decision_type(self, decisions: List[ExecutiveDecision]) -> str:
        """Find the most common type of decision."""
        decision_types = []
        for d in decisions:
            content = d.decision.lower()
            if 'threat' in content or 'danger' in content:
                decision_types.append('threat_response')
            elif 'investigate' in content or 'analyze' in content:
                decision_types.append('investigation')
            elif 'safe' in content or 'normal' in content:
                decision_types.append('routine')
            else:
                decision_types.append('strategic')

        from collections import Counter
        most_common = Counter(decision_types).most_common(1)
        return most_common[0][0] if most_common else 'mixed'

    def _parse_action_plan(self, response: str) -> List[Dict[str, Any]]:
        """Parse action plan from response."""
        # Simple parsing - could be more sophisticated
        lines = response.split('\n')
        steps = []

        for line in lines:
            line = line.strip()
            if line.startswith(("-", "*", "1.", "2.", "3.", "4.", "5.")):
                step_text = line.lstrip("-*123456789. ")
                steps.append({
                    "step": step_text,
                    "risk": "To be assessed",  # Could parse more details
                    "contingency": "To be planned"
                })

        return steps