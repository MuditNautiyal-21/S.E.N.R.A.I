import os
import sys
import requests

# Ensure 'tools' is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.command_toolkit import Toolset

class SENRAIAgent:
    def __init__(self, memory=None):
        self.memory = memory if memory else []
        self.toolkit = Toolset()
        self.llm_url = "http://localhost:5050/query"  # Flask proxy, not LM Studio directly

    def think(self, goal, context=""):
        prompt = f"""You are SENRAI — a Self-Evolving Neural Response Assistant Infrastructure.

RULES:
- You only take actions that are supported by your internal Toolset.
- Never assume access to mouse, keyboard, GUI, or internet unless a tool exists.
- If unsure about a command, ask the Toolset to handle it.
- Avoid hallucinations or fictional scenarios (e.g., "connecting to the system").

GOAL: {goal}
CONTEXT: {context}

Think: What should be the first step?
"""
        return self.query_llm(prompt)

    def plan(self, thought):
        prompt = f"""You are planning the next step based on this thought: "{thought}"

Create one specific and actionable step using your known tools only.
Only respond with a single valid plan.
"""
        return self.query_llm(prompt)

    def act(self, plan):
        lower_plan = plan.lower()

        if any(keyword in lower_plan for keyword in [
            "open", "launch", "search", "close", "terminate",
            "browser", "notepad", "calculator", "paint", "cmd", "vs code"
        ]):
            result = self.toolkit.run_tool(plan)
            if "not recognized" in result.lower() or "❌" in result:
                return f"[ABORTED] {result}"
            return result

        # LLM fallback for reasoning-only responses
        prompt = f"""You are SENRAI, and you're about to simulate the result of this plan:

PLAN: {plan}

RULES:
- Do NOT invent fictional UI actions like typing, mouse movement, or connecting to systems.
- Only describe outcomes that follow logically from the plan and available tool capabilities.
- If the action cannot be executed through Toolset, say so clearly.

Respond with what happens as a result:
"""
        return self.query_llm(prompt)

    def query_llm(self, prompt):
        try:
            payload = {
                "prompt": prompt  # ✅ Flask expects this structure
            }
            headers = {"Content-Type": "application/json"}
            res = requests.post(self.llm_url, json=payload, headers=headers)
            return res.json().get("response", "[No response from LLM]").strip()
        except Exception as e:
            return f"[ERROR] {e}"

    def run_agent_loop(self, goal, steps=3):
        full_log = []
        context = ""

        for i in range(steps):
            thought = self.think(goal, context)
            plan = self.plan(thought)
            result = self.act(plan)

            full_log.append((thought, plan, result))
            context += f"\nThought: {thought}\nPlan: {plan}\nResult: {result}\n"

            if "[ABORTED]" in result or "[ERROR]" in result:
                break

        return full_log
