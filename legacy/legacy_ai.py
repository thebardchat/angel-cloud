#!/usr/bin/env python3
"""
Legacy AI - Production Inference Engine
Custom AI assistant with persistent memory and operational context.
Uses locally trained models from 8TB drive.
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import firebase_admin
from firebase_admin import credentials, firestore

from config import config
from logger import LogiLogger

logger = LogiLogger.get_logger("legacy_ai")


class LegacyAI:
    """Production-ready AI assistant with operational memory"""

    def __init__(
        self,
        model_name: str = "legacy-ai-srm",
        memory_path: str = "/mnt/8tb_drive/legacy_ai/memory",
        ollama_url: str = None
    ):
        self.model_name = model_name
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)

        self.ollama_url = ollama_url or config.OLLAMA_BASE_URL
        self.db = None
        self.conversation_history = []
        self.session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        logger.info(f"Legacy AI initialized: {model_name}")
        logger.info(f"Session ID: {self.session_id}")

    def initialize_firebase(self):
        """Connect to Firestore for real-time data access"""
        if not firebase_admin._apps:
            cred = credentials.Certificate(config.CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        logger.info("Firestore connected for real-time data access")

    def get_active_drivers(self) -> List[Dict[str, Any]]:
        """Get current active drivers from Firestore"""
        collection_path = config.get_public_collection("drivers")
        docs = self.db.collection(collection_path).stream()

        drivers = []
        for doc in docs:
            data = doc.to_dict()
            if data.get('status') == 'active':
                drivers.append(data)

        return sorted(drivers, key=lambda d: d.get('haul_rate', 999))

    def get_operational_context(self) -> str:
        """Build context string with current operational data"""
        drivers = self.get_active_drivers()

        context = "CURRENT OPERATIONAL STATUS:\n\n"
        context += f"Active Drivers: {len(drivers)}\n\n"

        if drivers:
            context += "Top 5 Cost-Effective Drivers:\n"
            for i, driver in enumerate(drivers[:5], 1):
                context += f"{i}. {driver['name']} - ${driver['haul_rate']:.2f} ({driver['round_trip_minutes']} min RTM)\n"

        context += f"\nTimestamp: {datetime.utcnow().isoformat()}\n"

        return context

    def query(
        self,
        prompt: str,
        include_context: bool = True,
        temperature: float = 0.3
    ) -> Optional[str]:
        """
        Query Legacy AI with optional operational context.

        Args:
            prompt: User query
            include_context: Include real-time operational data
            temperature: Model temperature (0.0-1.0)

        Returns:
            AI response or None on error
        """
        # Build full prompt with context
        full_prompt = prompt

        if include_context and self.db:
            operational_context = self.get_operational_context()
            full_prompt = f"{operational_context}\n\nQuery: {prompt}"

        # Log query
        logger.info(f"Query: {prompt[:100]}...")

        try:
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_ctx": 4096
                    }
                },
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "")

                # Save to conversation history
                self.conversation_history.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "prompt": prompt,
                    "response": ai_response,
                    "model": self.model_name
                })

                logger.info(f"Response generated ({len(ai_response)} chars)")
                return ai_response
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None

        except requests.RequestException as e:
            logger.error(f"Failed to query model: {e}")
            return None

    def stream_query(self, prompt: str, include_context: bool = True):
        """
        Stream response from Legacy AI (for real-time output).
        Yields chunks of response as they're generated.
        """
        full_prompt = prompt

        if include_context and self.db:
            operational_context = self.get_operational_context()
            full_prompt = f"{operational_context}\n\nQuery: {prompt}"

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": True
                },
                stream=True,
                timeout=120
            )

            full_response = ""

            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "response" in chunk:
                        text = chunk["response"]
                        full_response += text
                        yield text

            # Save to history
            self.conversation_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "prompt": prompt,
                "response": full_response,
                "model": self.model_name
            })

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"\n[Error: {str(e)}]"

    def save_conversation(self):
        """Save conversation history to disk"""
        conversation_file = self.memory_path / f"session_{self.session_id}.json"

        with open(conversation_file, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "model": self.model_name,
                "created_at": datetime.utcnow().isoformat(),
                "conversation": self.conversation_history
            }, f, indent=2)

        logger.info(f"Conversation saved: {conversation_file}")
        return str(conversation_file)

    def load_conversation(self, session_id: str):
        """Load previous conversation"""
        conversation_file = self.memory_path / f"session_{session_id}.json"

        if conversation_file.exists():
            with open(conversation_file) as f:
                data = json.load(f)
                self.conversation_history = data.get("conversation", [])
                logger.info(f"Loaded {len(self.conversation_history)} messages")
        else:
            logger.warning(f"Conversation not found: {session_id}")

    def get_dispatch_recommendation(self, load_details: Dict[str, Any]) -> str:
        """
        Get AI recommendation for load dispatch.

        Args:
            load_details: {
                "weight_tons": 25,
                "destination": "Plant Code or Location",
                "priority": "cost" or "speed",
                "deadline": "ISO timestamp" (optional)
            }

        Returns:
            AI recommendation with specific driver assignment
        """
        weight = load_details.get("weight_tons", 25)
        destination = load_details.get("destination", "unknown")
        priority = load_details.get("priority", "cost")

        prompt = f"""I need to dispatch a {weight}-ton load to {destination}.
Priority: {priority}
Please recommend which driver to assign and explain why."""

        return self.query(prompt, include_context=True)

    def analyze_performance(self) -> str:
        """Analyze current fleet performance"""
        prompt = "Analyze the current driver performance and provide optimization recommendations."
        return self.query(prompt, include_context=True)

    def interactive_mode(self):
        """Interactive CLI for Legacy AI"""
        print("\n" + "=" * 60)
        print("LEGACY AI - Interactive Mode")
        print("=" * 60)
        print(f"Model: {self.model_name}")
        print(f"Session: {self.session_id}")
        print("\nCommands:")
        print("  'exit' - Quit")
        print("  'save' - Save conversation")
        print("  'context' - Show operational context")
        print("  'drivers' - List active drivers")
        print("=" * 60 + "\n")

        while True:
            try:
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                if user_input.lower() == 'exit':
                    self.save_conversation()
                    print("Conversation saved. Goodbye!")
                    break

                elif user_input.lower() == 'save':
                    file_path = self.save_conversation()
                    print(f"Saved: {file_path}")
                    continue

                elif user_input.lower() == 'context':
                    print("\n" + self.get_operational_context())
                    continue

                elif user_input.lower() == 'drivers':
                    drivers = self.get_active_drivers()
                    print(f"\nActive Drivers: {len(drivers)}")
                    for d in drivers:
                        print(f"  • {d['name']} - ${d['haul_rate']:.2f}")
                    continue

                # Stream AI response
                print("\nLegacy AI: ", end="", flush=True)
                for chunk in self.stream_query(user_input):
                    print(chunk, end="", flush=True)
                print()  # New line after response

            except KeyboardInterrupt:
                print("\n\nInterrupted. Use 'exit' to quit properly.")
                continue
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"\nError: {e}")


def main():
    """Main execution"""
    import sys

    logger.info("Legacy AI - Production Inference Engine")

    # Check for model name argument
    model_name = "legacy-ai-srm"
    if len(sys.argv) > 1:
        model_name = sys.argv[1]

    # Initialize Legacy AI
    memory_path = "/mnt/8tb_drive/legacy_ai/memory"
    if not Path("/mnt/8tb_drive").exists():
        logger.warning("8TB drive not mounted - using local memory")
        memory_path = "./ai_memory"

    ai = LegacyAI(
        model_name=model_name,
        memory_path=memory_path
    )

    # Initialize Firestore for real-time data
    if config.validate():
        ai.initialize_firebase()
    else:
        logger.warning("Skipping Firestore (credentials not configured)")

    # Run interactive mode
    ai.interactive_mode()


if __name__ == "__main__":
    main()
