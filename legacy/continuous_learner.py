#!/usr/bin/env python3
"""
Continuous Learner for Legacy AI
Automatically retrains models when new operational data is available.
Runs on schedule to keep AI current with latest dispatch patterns.
"""

import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

from training_data_builder import TrainingDataBuilder
from model_trainer import ModelTrainer
from model_manager import ModelManager
from logger import LogiLogger

logger = LogiLogger.get_logger("continuous_learner")


class ContinuousLearner:
    """Automated continuous learning pipeline"""

    def __init__(
        self,
        retrain_interval_days: int = 7,
        min_new_examples: int = 50,
        auto_deploy: bool = False
    ):
        self.retrain_interval = timedelta(days=retrain_interval_days)
        self.min_new_examples = min_new_examples
        self.auto_deploy = auto_deploy

        # Initialize components
        self.data_builder = TrainingDataBuilder()
        self.trainer = ModelTrainer()
        self.model_manager = ModelManager()

        self.last_train_time = None
        self.load_state()

        logger.info(f"Continuous Learner initialized")
        logger.info(f"Retrain interval: {retrain_interval_days} days")
        logger.info(f"Min new examples: {min_new_examples}")
        logger.info(f"Auto-deploy: {auto_deploy}")

    def load_state(self):
        """Load last training timestamp"""
        state_file = self.data_builder.output_dir / "learner_state.json"

        if state_file.exists():
            import json
            with open(state_file) as f:
                state = json.load(f)
                self.last_train_time = datetime.fromisoformat(state.get("last_train_time"))
                logger.info(f"Last training: {self.last_train_time}")

    def save_state(self):
        """Save training state"""
        import json
        state_file = self.data_builder.output_dir / "learner_state.json"

        with open(state_file, 'w') as f:
            json.dump({
                "last_train_time": datetime.utcnow().isoformat()
            }, f, indent=2)

    def should_retrain(self) -> bool:
        """Determine if retraining is needed"""
        if self.last_train_time is None:
            logger.info("First training run")
            return True

        time_since_last = datetime.utcnow() - self.last_train_time

        if time_since_last >= self.retrain_interval:
            logger.info(f"Retrain interval reached ({time_since_last.days} days)")
            return True

        logger.info(f"Next retrain in {(self.retrain_interval - time_since_last).days} days")
        return False

    def check_new_data(self) -> int:
        """Check for new training examples"""
        # This would check Firestore for new data since last training
        # For now, return a placeholder
        logger.info("Checking for new operational data...")

        # Count new driver/plant records
        self.data_builder.initialize_firebase()
        drivers = self.data_builder.fetch_driver_data()
        plants = self.data_builder.fetch_plant_data()

        # Rough estimate of new examples
        new_examples = len(drivers) * 3 + len(plants)  # 3 examples per driver

        logger.info(f"Estimated new examples: {new_examples}")
        return new_examples

    def run_training_cycle(self) -> bool:
        """Execute full training cycle"""
        logger.info("=" * 60)
        logger.info("STARTING CONTINUOUS LEARNING CYCLE")
        logger.info("=" * 60)

        try:
            # Step 1: Build fresh datasets
            logger.info("Step 1: Building training datasets...")
            datasets = self.data_builder.build_all_datasets()

            # Step 2: Train model
            logger.info("Step 2: Training model...")
            success = self.trainer.train_legacy_ai()

            if not success:
                logger.error("Training failed")
                return False

            # Step 3: Get latest model name
            import subprocess
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True
            )

            # Find latest legacy-ai model
            latest_model = None
            for line in result.stdout.split('\n'):
                if 'legacy-ai-srm' in line:
                    latest_model = line.split()[0]
                    break

            if not latest_model:
                logger.error("Could not find trained model")
                return False

            # Step 4: Register model
            logger.info(f"Step 3: Registering model {latest_model}...")
            self.model_manager.register_model(
                latest_model,
                {
                    "training_method": "continuous_learning",
                    "datasets": datasets,
                    "trained_at": datetime.utcnow().isoformat()
                },
                set_active=self.auto_deploy
            )

            # Step 5: Auto-deploy if enabled
            if self.auto_deploy:
                logger.info("Step 4: Auto-deploying model to production...")
                self.model_manager.set_active_model(latest_model)
                logger.info(f"✓ Model deployed: {latest_model}")
            else:
                logger.info("Manual deployment required")
                logger.info(f"To deploy: python3 model_manager.py set-active {latest_model}")

            # Save state
            self.save_state()
            self.last_train_time = datetime.utcnow()

            logger.info("=" * 60)
            logger.info("CONTINUOUS LEARNING CYCLE COMPLETE")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"Training cycle failed: {e}", exc_info=True)
            return False

    def run_once(self):
        """Run single learning cycle"""
        if self.should_retrain():
            new_examples = self.check_new_data()

            if new_examples >= self.min_new_examples:
                logger.info(f"Sufficient new data ({new_examples} examples) - starting training")
                return self.run_training_cycle()
            else:
                logger.info(f"Insufficient new data ({new_examples}/{self.min_new_examples}) - skipping")
                return False
        else:
            logger.info("Retrain interval not reached - skipping")
            return False

    def run_continuous(self, check_interval_hours: int = 24):
        """Run continuous learning loop"""
        logger.info(f"Starting continuous learning mode (check every {check_interval_hours}h)")

        while True:
            try:
                self.run_once()

                # Wait for next check
                logger.info(f"Sleeping for {check_interval_hours} hours...")
                time.sleep(check_interval_hours * 3600)

            except KeyboardInterrupt:
                logger.info("Continuous learning stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous loop: {e}")
                time.sleep(3600)  # Wait 1 hour on error


def main():
    """Main execution"""
    import sys

    logger.info("Legacy AI Continuous Learner")

    # Parse arguments
    mode = sys.argv[1] if len(sys.argv) > 1 else "once"

    learner = ContinuousLearner(
        retrain_interval_days=7,
        min_new_examples=50,
        auto_deploy=False  # Set True for automatic deployment
    )

    if mode == "continuous":
        learner.run_continuous(check_interval_hours=24)
    else:
        success = learner.run_once()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
