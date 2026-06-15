#!/usr/bin/env python3
"""
Training Data Builder for Legacy AI
Aggregates operational data from Firestore and Google Sheets into training datasets.
Prepares data for fine-tuning local Llama models on dispatch optimization.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import csv

import firebase_admin
from firebase_admin import credentials, firestore

from config import config
from logger import LogiLogger

logger = LogiLogger.get_logger("training_data")


class TrainingDataBuilder:
    """Build training datasets from operational data"""

    def __init__(self, output_dir: str = "/mnt/8tb_drive/legacy_ai/datasets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db = None
        logger.info(f"Training data builder initialized: {self.output_dir}")

    def initialize_firebase(self):
        """Initialize Firestore connection"""
        if not firebase_admin._apps:
            cred = credentials.Certificate(config.CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        logger.info("Firestore initialized for training data collection")

    def fetch_driver_data(self) -> List[Dict[str, Any]]:
        """Fetch all driver data from Firestore"""
        collection_path = config.get_public_collection("drivers")
        docs = self.db.collection(collection_path).stream()

        drivers = []
        for doc in docs:
            data = doc.to_dict()
            drivers.append(data)

        logger.info(f"Fetched {len(drivers)} driver records")
        return drivers

    def fetch_plant_data(self) -> List[Dict[str, Any]]:
        """Fetch all plant data from Firestore"""
        collection_path = config.get_public_collection("plants")
        docs = self.db.collection(collection_path).stream()

        plants = []
        for doc in docs:
            data = doc.to_dict()
            plants.append(data)

        logger.info(f"Fetched {len(plants)} plant records")
        return plants

    def create_dispatch_optimization_dataset(self) -> str:
        """
        Create training dataset for dispatch optimization.
        Format: instruction-following pairs for Llama fine-tuning.
        """
        drivers = self.fetch_driver_data()
        plants = self.fetch_plant_data()

        dataset = []

        # Generate training examples from driver data
        for driver in drivers:
            # Example 1: Haul rate calculation
            instruction = f"Calculate the haul rate for driver {driver['name']} with a round trip time of {driver['round_trip_minutes']} minutes."
            output = f"For {driver['name']} with {driver['round_trip_minutes']} minutes round trip:\n"\
                     f"Rate = ($130 / 60 mins) × {driver['round_trip_minutes']} / 25 tons = ${driver['haul_rate']:.2f}\n"\
                     f"Status: {driver['status']}"

            dataset.append({
                "instruction": instruction,
                "input": "",
                "output": output,
                "context": "SRM Dispatch - Haul Rate Calculation"
            })

            # Example 2: Driver availability
            if driver['status'] == 'active':
                instruction = f"Is driver {driver['name']} available for dispatch?"
                output = f"Yes, {driver['name']} is {driver['status']} with a haul rate of ${driver['haul_rate']:.2f} " \
                         f"based on {driver['round_trip_minutes']} minute round trips."
            else:
                instruction = f"Can we assign {driver['name']} to a new load?"
                output = f"No, {driver['name']} is currently {driver['status']}. Consider assigning an active driver."

            dataset.append({
                "instruction": instruction,
                "input": "",
                "output": output,
                "context": "SRM Dispatch - Driver Availability"
            })

            # Example 3: Cost optimization
            instruction = f"What is the cost per ton for {driver['name']}?"
            cost_per_ton = driver['haul_rate']  # Already per 25 tons
            output = f"Driver {driver['name']} has a haul rate of ${driver['haul_rate']:.2f} per 25-ton load, " \
                     f"which equals ${cost_per_ton/25:.2f} per ton."

            dataset.append({
                "instruction": instruction,
                "input": "",
                "output": output,
                "context": "SRM Dispatch - Cost Analysis"
            })

        # Generate training examples for route optimization
        for plant in plants:
            instruction = f"What plant should I use for deliveries to {plant['location']}?"
            output = f"For deliveries to {plant['location']}, use {plant['name']} (Plant Code: {plant['code']})."

            dataset.append({
                "instruction": instruction,
                "input": "",
                "output": output,
                "context": "SRM Dispatch - Route Planning"
            })

        # Generate comparative analysis examples
        sorted_drivers = sorted(drivers, key=lambda d: d.get('haul_rate', 999))
        if len(sorted_drivers) >= 3:
            instruction = "Which drivers have the most cost-effective haul rates?"
            top_3 = sorted_drivers[:3]
            output = "Most cost-effective drivers:\n"
            for i, d in enumerate(top_3, 1):
                output += f"{i}. {d['name']} - ${d['haul_rate']:.2f} ({d['round_trip_minutes']} min RTM)\n"

            dataset.append({
                "instruction": instruction,
                "input": "",
                "output": output,
                "context": "SRM Dispatch - Driver Comparison"
            })

        # Save dataset
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"dispatch_optimization_{timestamp}.jsonl"

        with open(output_file, 'w') as f:
            for item in dataset:
                f.write(json.dumps(item) + '\n')

        logger.info(f"Created dispatch optimization dataset: {output_file}")
        logger.info(f"Total training examples: {len(dataset)}")

        return str(output_file)

    def create_shanebrain_memory_dataset(self) -> str:
        """
        Create training dataset from Shanebrain memory and operational patterns.
        This teaches the AI Shane's preferences and decision-making style.
        """
        dataset = []

        # Load mission statement
        mission_file = Path(__file__).parent / "ai-mission-statement.md"
        if mission_file.exists():
            with open(mission_file) as f:
                mission_content = f.read()

            # Create context-aware examples
            dataset.append({
                "instruction": "What is the primary mission of LogiBot?",
                "input": "",
                "output": "LogiBot's mission is to build fixed-cost local AI infrastructure to replace $1,000/mo variable cloud costs. "
                          "The system uses local Llama 3.2 via Ollama on Ubuntu WSL/USB, with Firestore for persistence and "
                          "Google Sheets as the data source for SRM Operations.",
                "context": "Shanebrain - System Architecture"
            })

            dataset.append({
                "instruction": "Explain the haul rate calculation formula.",
                "input": "",
                "output": "Haul Rate = ($130 / 60 minutes) × Round Trip Minutes / 25 tons. "
                          "The result is rounded up to the nearest $0.50 with a minimum of $6.00. "
                          "This formula ensures fair pricing based on time and tonnage.",
                "context": "Shanebrain - Business Logic"
            })

            dataset.append({
                "instruction": "What are the Firestore storage rules?",
                "input": "",
                "output": "Public data: /artifacts/{appId}/public/data/{collectionName}\n"
                          "Private data: /artifacts/{appId}/users/{userId}/{collectionName}\n"
                          "CRITICAL: No complex queries. Fetch all documents and filter in memory.",
                "context": "Shanebrain - Data Architecture"
            })

        # Communication style examples (Shane's protocol)
        dataset.extend([
            {
                "instruction": "How should you communicate with Shane?",
                "input": "",
                "output": "Mandatory directness. No apologies. No conversational filler. No summaries. No rants. "
                          "No repetition. Prioritize code execution over explanation. If the conversation gets repetitive, "
                          "stop and wait for reset.",
                "context": "Shanebrain - Communication Protocol"
            },
            {
                "instruction": "What is Shane's role?",
                "input": "",
                "output": "Shane Brazelton is the Systems Architect and Dispatch Manager at SRM Trucking. "
                          "He's building LogiBot to eliminate $1,000/mo cloud costs while maintaining operational efficiency.",
                "context": "Shanebrain - User Profile"
            }
        ])

        # Save dataset
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"shanebrain_memory_{timestamp}.jsonl"

        with open(output_file, 'w') as f:
            for item in dataset:
                f.write(json.dumps(item) + '\n')

        logger.info(f"Created Shanebrain memory dataset: {output_file}")
        logger.info(f"Total memory examples: {len(dataset)}")

        return str(output_file)

    def create_decision_pattern_dataset(self) -> str:
        """
        Create dataset from historical decision patterns.
        This trains the AI to make decisions like Shane would.
        """
        drivers = self.fetch_driver_data()
        dataset = []

        # Decision pattern: Driver assignment based on cost and availability
        active_drivers = [d for d in drivers if d.get('status') == 'active']
        if active_drivers:
            sorted_by_rate = sorted(active_drivers, key=lambda d: d.get('haul_rate', 999))

            instruction = "I have a 25-ton load going 90 minutes round trip. Which driver should I assign?"
            best_driver = sorted_by_rate[0] if sorted_by_rate else None

            if best_driver:
                output = f"Assign {best_driver['name']}. They have the most cost-effective rate at ${best_driver['haul_rate']:.2f} " \
                         f"and are currently active. For a 90-minute round trip, the cost will be approximately ${best_driver['haul_rate']:.2f}."
            else:
                output = "No active drivers available. Check driver availability before dispatching."

            dataset.append({
                "instruction": instruction,
                "input": "",
                "output": output,
                "context": "Decision Pattern - Load Assignment"
            })

        # Decision pattern: Cost vs. time tradeoffs
        if len(active_drivers) >= 2:
            fastest = min(active_drivers, key=lambda d: d.get('round_trip_minutes', 999))
            cheapest = min(active_drivers, key=lambda d: d.get('haul_rate', 999))

            instruction = "Should I prioritize cost or speed for this delivery?"
            output = f"For cost optimization: Use {cheapest['name']} (${cheapest['haul_rate']:.2f})\n" \
                     f"For speed: Use {fastest['name']} ({fastest['round_trip_minutes']} min RTM)\n" \
                     f"Decision depends on customer priority and deadline constraints."

            dataset.append({
                "instruction": instruction,
                "input": "",
                "output": output,
                "context": "Decision Pattern - Optimization Strategy"
            })

        # Save dataset
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"decision_patterns_{timestamp}.jsonl"

        with open(output_file, 'w') as f:
            for item in dataset:
                f.write(json.dumps(item) + '\n')

        logger.info(f"Created decision pattern dataset: {output_file}")
        logger.info(f"Total decision examples: {len(dataset)}")

        return str(output_file)

    def merge_datasets(self, output_name: str = "legacy_ai_complete") -> str:
        """
        Merge all dataset types into a single comprehensive training file.
        """
        all_files = list(self.output_dir.glob("*.jsonl"))
        merged_data = []

        for file_path in all_files:
            if "complete" in file_path.name:
                continue  # Skip previously merged files

            with open(file_path) as f:
                for line in f:
                    merged_data.append(json.loads(line))

        # Shuffle for better training
        import random
        random.shuffle(merged_data)

        # Save merged dataset
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"{output_name}_{timestamp}.jsonl"

        with open(output_file, 'w') as f:
            for item in merged_data:
                f.write(json.dumps(item) + '\n')

        logger.info(f"Merged {len(all_files)} datasets into: {output_file}")
        logger.info(f"Total examples in merged dataset: {len(merged_data)}")

        # Create training/validation split
        split_idx = int(len(merged_data) * 0.9)  # 90% train, 10% validation
        train_data = merged_data[:split_idx]
        val_data = merged_data[split_idx:]

        train_file = self.output_dir / f"{output_name}_train_{timestamp}.jsonl"
        val_file = self.output_dir / f"{output_name}_val_{timestamp}.jsonl"

        with open(train_file, 'w') as f:
            for item in train_data:
                f.write(json.dumps(item) + '\n')

        with open(val_file, 'w') as f:
            for item in val_data:
                f.write(json.dumps(item) + '\n')

        logger.info(f"Created train/val split: {len(train_data)} train, {len(val_data)} validation")

        return str(output_file)

    def generate_training_metadata(self) -> Dict[str, Any]:
        """Generate metadata about training data"""
        all_files = list(self.output_dir.glob("*.jsonl"))

        metadata = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_datasets": len(all_files),
            "datasets": [],
            "total_examples": 0
        }

        for file_path in all_files:
            with open(file_path) as f:
                lines = f.readlines()
                example_count = len(lines)
                metadata["total_examples"] += example_count

                metadata["datasets"].append({
                    "filename": file_path.name,
                    "examples": example_count,
                    "size_mb": file_path.stat().st_size / (1024 * 1024)
                })

        # Save metadata
        metadata_file = self.output_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Generated training metadata: {metadata_file}")
        return metadata

    def build_all_datasets(self) -> Dict[str, str]:
        """Build all training datasets"""
        logger.info("=" * 60)
        logger.info("Starting comprehensive training data build")
        logger.info("=" * 60)

        self.initialize_firebase()

        results = {
            "dispatch_optimization": self.create_dispatch_optimization_dataset(),
            "shanebrain_memory": self.create_shanebrain_memory_dataset(),
            "decision_patterns": self.create_decision_pattern_dataset(),
        }

        # Merge all datasets
        results["merged_dataset"] = self.merge_datasets()

        # Generate metadata
        metadata = self.generate_training_metadata()

        logger.info("=" * 60)
        logger.info(f"Training data build complete: {metadata['total_examples']} total examples")
        logger.info("=" * 60)

        return results


def main():
    """Main execution"""
    logger.info("Training Data Builder for Legacy AI")

    # Check for 8TB drive mount
    default_path = "/mnt/8tb_drive/legacy_ai/datasets"
    if not Path("/mnt/8tb_drive").exists():
        logger.warning("8TB drive not found at /mnt/8tb_drive - using local storage")
        default_path = "./training_datasets"

    builder = TrainingDataBuilder(output_dir=default_path)
    results = builder.build_all_datasets()

    print("\n" + "=" * 60)
    print("TRAINING DATASETS CREATED")
    print("=" * 60)
    for name, path in results.items():
        print(f"{name}: {path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
