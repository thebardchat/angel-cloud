#!/usr/bin/env python3
"""
Model Version Manager for Legacy AI
Handles model versioning, deployment, and lifecycle management on 8TB drive.
"""

import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from logger import LogiLogger

logger = LogiLogger.get_logger("model_manager")


class ModelManager:
    """Manage trained model versions and deployments"""

    def __init__(self, model_dir: str = "/mnt/8tb_drive/legacy_ai/models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.model_dir / "model_registry.json"
        self.registry = self.load_registry()

        logger.info(f"Model Manager initialized: {model_dir}")

    def load_registry(self) -> Dict[str, Any]:
        """Load model registry"""
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                return json.load(f)
        return {"models": [], "active_model": None}

    def save_registry(self):
        """Save model registry"""
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)

    def register_model(
        self,
        model_name: str,
        metadata: Dict[str, Any],
        set_active: bool = False
    ):
        """Register a new model version"""
        model_entry = {
            "name": model_name,
            "registered_at": datetime.utcnow().isoformat(),
            "metadata": metadata,
            "status": "active" if set_active else "available"
        }

        self.registry["models"].append(model_entry)

        if set_active:
            self.registry["active_model"] = model_name

        self.save_registry()
        logger.info(f"Registered model: {model_name}")

    def list_models(self) -> List[Dict[str, Any]]:
        """List all registered models"""
        return self.registry["models"]

    def get_active_model(self) -> Optional[str]:
        """Get currently active model name"""
        return self.registry.get("active_model")

    def set_active_model(self, model_name: str) -> bool:
        """Set active model for production use"""
        # Verify model exists in Ollama
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True
            )

            if model_name in result.stdout:
                self.registry["active_model"] = model_name
                self.save_registry()
                logger.info(f"Active model set to: {model_name}")
                return True
            else:
                logger.error(f"Model not found in Ollama: {model_name}")
                return False

        except Exception as e:
            logger.error(f"Error setting active model: {e}")
            return False

    def delete_model(self, model_name: str) -> bool:
        """Delete model from Ollama and registry"""
        try:
            # Remove from Ollama
            result = subprocess.run(
                ["ollama", "rm", model_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # Remove from registry
                self.registry["models"] = [
                    m for m in self.registry["models"]
                    if m["name"] != model_name
                ]

                if self.registry.get("active_model") == model_name:
                    self.registry["active_model"] = None

                self.save_registry()
                logger.info(f"Deleted model: {model_name}")
                return True
            else:
                logger.error(f"Failed to delete model: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error deleting model: {e}")
            return False

    def cleanup_old_models(self, keep_last_n: int = 5):
        """Remove old model versions, keeping only the N most recent"""
        models = sorted(
            self.registry["models"],
            key=lambda m: m["registered_at"],
            reverse=True
        )

        active_model = self.get_active_model()
        models_to_delete = []

        for model in models[keep_last_n:]:
            if model["name"] != active_model:
                models_to_delete.append(model["name"])

        for model_name in models_to_delete:
            logger.info(f"Cleaning up old model: {model_name}")
            self.delete_model(model_name)

        logger.info(f"Cleanup complete. Removed {len(models_to_delete)} old models")

    def export_model(self, model_name: str, export_path: str) -> bool:
        """Export model for sharing or backup"""
        logger.info(f"Exporting model {model_name} to {export_path}")

        try:
            # Use ollama show to get model details
            result = subprocess.run(
                ["ollama", "show", model_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                export_dir = Path(export_path)
                export_dir.mkdir(parents=True, exist_ok=True)

                # Save model info
                info_file = export_dir / f"{model_name}_info.txt"
                with open(info_file, 'w') as f:
                    f.write(result.stdout)

                logger.info(f"Model exported to: {export_path}")
                return True
            else:
                logger.error(f"Failed to export model: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error exporting model: {e}")
            return False

    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about model usage and performance"""
        stats = {
            "total_models": len(self.registry["models"]),
            "active_model": self.get_active_model(),
            "models": []
        }

        for model in self.registry["models"]:
            metadata_file = self.model_dir / f"{model['name']}_metadata.json"

            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    stats["models"].append({
                        "name": model["name"],
                        "registered": model["registered_at"],
                        "dataset": metadata.get("dataset_path", "unknown"),
                        "metrics": metadata.get("metrics", {})
                    })

        return stats

    def compare_models(self, model_a: str, model_b: str) -> Dict[str, Any]:
        """Compare two model versions"""
        comparison = {
            "model_a": model_a,
            "model_b": model_b,
            "differences": []
        }

        # Load metadata for both
        metadata_a_file = self.model_dir / f"{model_a}_metadata.json"
        metadata_b_file = self.model_dir / f"{model_b}_metadata.json"

        if metadata_a_file.exists() and metadata_b_file.exists():
            with open(metadata_a_file) as f:
                meta_a = json.load(f)
            with open(metadata_b_file) as f:
                meta_b = json.load(f)

            comparison["metadata_a"] = meta_a
            comparison["metadata_b"] = meta_b

            # Compare key metrics
            if "metrics" in meta_a and "metrics" in meta_b:
                comparison["differences"].append({
                    "field": "metrics",
                    "model_a": meta_a["metrics"],
                    "model_b": meta_b["metrics"]
                })

        return comparison


def main():
    """Main execution"""
    manager = ModelManager()

    print("\n" + "=" * 60)
    print("LEGACY AI MODEL MANAGER")
    print("=" * 60)

    stats = manager.get_model_stats()

    print(f"\nTotal Models: {stats['total_models']}")
    print(f"Active Model: {stats['active_model']}")

    print("\nRegistered Models:")
    for model in stats["models"]:
        status = "✓ ACTIVE" if model["name"] == stats["active_model"] else "  "
        print(f"{status} {model['name']}")
        print(f"    Registered: {model['registered']}")
        print(f"    Dataset: {Path(model['dataset']).name}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
