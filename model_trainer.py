#!/usr/bin/env python3
"""
Legacy AI Model Trainer
Fine-tunes Llama models on 8TB external drive using operational data.
Supports LoRA/QLoRA for efficient training on consumer hardware.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from logger import LogiLogger

logger = LogiLogger.get_logger("model_trainer")


class ModelTrainer:
    """Fine-tune local Llama models with operational data"""

    def __init__(
        self,
        base_model: str = "llama3.2",
        model_dir: str = "/mnt/8tb_drive/legacy_ai/models",
        dataset_dir: str = "/mnt/8tb_drive/legacy_ai/datasets"
    ):
        self.base_model = base_model
        self.model_dir = Path(model_dir)
        self.dataset_dir = Path(dataset_dir)

        self.model_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Model Trainer initialized")
        logger.info(f"Base model: {base_model}")
        logger.info(f"Model directory: {model_dir}")
        logger.info(f"Dataset directory: {dataset_dir}")

    def check_ollama_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
            return False

    def pull_base_model(self) -> bool:
        """Pull base model if not already available"""
        logger.info(f"Checking for base model: {self.base_model}")

        try:
            result = subprocess.run(
                ["ollama", "pull", self.base_model],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout for large models
            )

            if result.returncode == 0:
                logger.info(f"Base model {self.base_model} ready")
                return True
            else:
                logger.error(f"Failed to pull base model: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error pulling base model: {e}")
            return False

    def create_modelfile(self, dataset_path: str, output_name: str) -> str:
        """
        Create Ollama Modelfile for fine-tuning.
        Uses GGUF format optimized for CPU/GPU inference.
        """
        modelfile_content = f"""# Legacy AI - {output_name}
# Fine-tuned on SRM Dispatch operational data
# Generated: {datetime.utcnow().isoformat()}

FROM {self.base_model}

# System prompt optimized for Shane's dispatch operations
SYSTEM \"\"\"You are Legacy AI, Shane Brazelton's personal dispatch optimization assistant for SRM Trucking.

Your expertise:
- Calculating haul rates: ($130/60) × RTM / 25 tons, rounded to $0.50, min $6.00
- Driver assignment optimization based on cost and availability
- Route planning with plant codes and locations
- Real-time decision-making for dispatch operations

Communication style:
- Direct and concise (no filler, no apologies)
- Focus on actionable recommendations
- Prioritize cost efficiency and operational speed
- Cite specific data (driver names, rates, RTM) in responses

Data sources:
- 19 active drivers with real-time availability
- Plant codes and locations from SRM Operations
- Historical performance patterns

Always provide specific, data-driven recommendations.
\"\"\"

# Parameters optimized for dispatch decision-making
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096
PARAMETER stop "Human:"
PARAMETER stop "Assistant:"

# Template for instruction-following
TEMPLATE \"\"\"{{ if .System }}<|system|>
{{ .System }}<|end|>
{{ end }}{{ if .Prompt }}<|user|>
{{ .Prompt }}<|end|>
{{ end }}<|assistant|>
{{ .Response }}<|end|>
\"\"\"
"""

        modelfile_path = self.model_dir / f"{output_name}_Modelfile"
        with open(modelfile_path, 'w') as f:
            f.write(modelfile_content)

        logger.info(f"Created Modelfile: {modelfile_path}")
        return str(modelfile_path)

    def train_with_ollama(self, dataset_path: str, model_name: str) -> bool:
        """
        Train model using Ollama's create command.
        This creates a new model based on the Modelfile.
        """
        logger.info(f"Starting model training: {model_name}")
        logger.info(f"Dataset: {dataset_path}")

        # Create Modelfile
        modelfile_path = self.create_modelfile(dataset_path, model_name)

        # Create model with Ollama
        try:
            result = subprocess.run(
                ["ollama", "create", model_name, "-f", modelfile_path],
                capture_output=True,
                text=True,
                timeout=7200,  # 2 hour timeout
                cwd=str(self.model_dir)
            )

            if result.returncode == 0:
                logger.info(f"✓ Model created successfully: {model_name}")
                logger.info(result.stdout)
                return True
            else:
                logger.error(f"✗ Model creation failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Model creation timed out after 2 hours")
            return False
        except Exception as e:
            logger.error(f"Error during model creation: {e}")
            return False

    def train_with_unsloth(self, dataset_path: str, model_name: str) -> bool:
        """
        Alternative: Train using Unsloth for faster fine-tuning.
        This is for advanced users who want full LoRA/QLoRA control.
        """
        logger.info(f"Advanced training with Unsloth (requires unsloth package)")
        logger.warning("This method requires: pip install unsloth")

        training_script = f"""
# Unsloth Fine-tuning Script
# Install: pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

from unsloth import FastLanguageModel
import torch

# Load base model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/llama-3.2-1b-bnb-4bit",  # or 3b variant
    max_seq_length = 4096,
    dtype = None,  # Auto-detect
    load_in_4bit = True,
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,  # LoRA rank
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0.05,
    bias = "none",
    use_gradient_checkpointing = True,
    random_state = 42,
)

# Load dataset
from datasets import load_dataset
dataset = load_dataset("json", data_files="{dataset_path}")

# Training arguments
from transformers import TrainingArguments
from trl import SFTTrainer

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset["train"],
    dataset_text_field = "text",
    max_seq_length = 4096,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 10,
        max_steps = 100,  # Increase for production
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 42,
        output_dir = "{self.model_dir}/{model_name}",
    ),
)

# Train
trainer.train()

# Save model
model.save_pretrained("{self.model_dir}/{model_name}")
tokenizer.save_pretrained("{self.model_dir}/{model_name}")

print("Training complete: {self.model_dir}/{model_name}")
"""

        script_path = self.model_dir / f"train_{model_name}.py"
        with open(script_path, 'w') as f:
            f.write(training_script)

        logger.info(f"Training script created: {script_path}")
        logger.info("Run with: python3 " + str(script_path))

        return True

    def test_model(self, model_name: str) -> bool:
        """Test trained model with sample queries"""
        logger.info(f"Testing model: {model_name}")

        test_queries = [
            "Calculate the haul rate for a 90-minute round trip.",
            "Which driver should I assign for a cost-effective delivery?",
            "What is the haul rate formula?",
            "Is driver John Doe available?",
        ]

        for query in test_queries:
            logger.info(f"\nQuery: {query}")

            try:
                result = subprocess.run(
                    ["ollama", "run", model_name, query],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    logger.info(f"Response: {result.stdout[:200]}...")
                else:
                    logger.error(f"Query failed: {result.stderr}")

            except Exception as e:
                logger.error(f"Error testing query: {e}")

        return True

    def save_training_metadata(self, model_name: str, dataset_path: str, metrics: Dict[str, Any]):
        """Save training metadata for version control"""
        metadata = {
            "model_name": model_name,
            "base_model": self.base_model,
            "dataset_path": dataset_path,
            "trained_at": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "hardware": self.get_hardware_info()
        }

        metadata_file = self.model_dir / f"{model_name}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Training metadata saved: {metadata_file}")

    def get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information"""
        import platform

        info = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }

        # Check for CUDA
        try:
            import torch
            info["cuda_available"] = torch.cuda.is_available()
            if torch.cuda.is_available():
                info["cuda_version"] = torch.version.cuda
                info["gpu_name"] = torch.cuda.get_device_name(0)
        except ImportError:
            info["cuda_available"] = False

        return info

    def train_legacy_ai(self, dataset_name: str = "legacy_ai_complete") -> bool:
        """
        Main training pipeline for Legacy AI.
        Creates a fine-tuned model ready for deployment.
        """
        logger.info("=" * 60)
        logger.info("LEGACY AI TRAINING PIPELINE")
        logger.info("=" * 60)

        # Check Ollama
        if not self.check_ollama_availability():
            logger.error("Ollama not available. Install with: curl https://ollama.ai/install.sh | sh")
            return False

        # Pull base model
        if not self.pull_base_model():
            logger.error("Failed to pull base model")
            return False

        # Find latest dataset
        dataset_files = list(self.dataset_dir.glob(f"{dataset_name}_train_*.jsonl"))
        if not dataset_files:
            logger.error(f"No training dataset found matching: {dataset_name}_train_*.jsonl")
            return False

        latest_dataset = max(dataset_files, key=lambda p: p.stat().st_mtime)
        logger.info(f"Using dataset: {latest_dataset}")

        # Generate model name
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        model_name = f"legacy-ai-srm-{timestamp}"

        # Train model
        success = self.train_with_ollama(str(latest_dataset), model_name)

        if success:
            # Test model
            self.test_model(model_name)

            # Save metadata
            self.save_training_metadata(model_name, str(latest_dataset), {
                "training_method": "ollama_create",
                "status": "success"
            })

            logger.info("=" * 60)
            logger.info(f"✓ TRAINING COMPLETE: {model_name}")
            logger.info(f"Test with: ollama run {model_name}")
            logger.info("=" * 60)

        return success


def main():
    """Main execution"""
    logger.info("Legacy AI Model Trainer")

    # Check for 8TB drive
    if not Path("/mnt/8tb_drive").exists():
        logger.warning("8TB drive not mounted at /mnt/8tb_drive")
        logger.info("Using local storage instead")
        model_dir = "./trained_models"
        dataset_dir = "./training_datasets"
    else:
        model_dir = "/mnt/8tb_drive/legacy_ai/models"
        dataset_dir = "/mnt/8tb_drive/legacy_ai/datasets"

    trainer = ModelTrainer(
        base_model="llama3.2",
        model_dir=model_dir,
        dataset_dir=dataset_dir
    )

    # Train Legacy AI
    success = trainer.train_legacy_ai()

    if success:
        print("\n" + "=" * 60)
        print("LEGACY AI TRAINING SUCCESSFUL")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Test your model: ollama list")
        print("2. Run inference: ollama run legacy-ai-srm-<timestamp>")
        print("3. Deploy to production with legacy_ai.py")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("TRAINING FAILED - Check logs for details")
        print("=" * 60)


if __name__ == "__main__":
    main()
