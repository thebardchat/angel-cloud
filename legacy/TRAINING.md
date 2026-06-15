## Legacy AI Training System

**Train custom AI models on your 8TB drive with your operational data**

---

## Overview

The Legacy AI training system transforms your SRM dispatch data into a personalized AI assistant that learns your operational patterns and decision-making style.

### What You'll Build

- **Custom Llama Model** fine-tuned on your dispatch data
- **Persistent Memory** stored on 8TB external drive
- **Continuous Learning** automatic retraining with new data
- **Production-Ready Inference** optimized for local deployment

### Hardware Requirements

- **Storage**: 8TB external drive (recommended) or 100GB+ local storage
- **RAM**: 16GB minimum, 32GB recommended
- **CPU**: Modern multi-core processor (8+ threads)
- **GPU**: Optional (NVIDIA with 8GB+ VRAM for faster training)

---

## Quick Start

### 1. Mount 8TB Drive

```bash
# Linux/WSL
sudo mkdir -p /mnt/8tb_drive
sudo mount /dev/sdX1 /mnt/8tb_drive  # Replace sdX1 with your drive

# Verify mount
df -h | grep 8tb
```

### 2. Install Ollama

```bash
curl https://ollama.ai/install.sh | sh

# Verify installation
ollama --version

# Pull base model
ollama pull llama3.2
```

### 3. Build Training Datasets

```bash
# Activate virtual environment
source venv/bin/activate

# Build datasets from operational data
python3 training_data_builder.py
```

**Output:**
- `/mnt/8tb_drive/legacy_ai/datasets/dispatch_optimization_*.jsonl`
- `/mnt/8tb_drive/legacy_ai/datasets/shanebrain_memory_*.jsonl`
- `/mnt/8tb_drive/legacy_ai/datasets/decision_patterns_*.jsonl`
- `/mnt/8tb_drive/legacy_ai/datasets/legacy_ai_complete_*.jsonl` (merged)

### 4. Train Your Model

```bash
python3 model_trainer.py
```

**Training Time:**
- **Ollama Method**: 5-15 minutes (CPU)
- **Unsloth Method**: 30-60 minutes (GPU, advanced)

**Output:**
- Model: `legacy-ai-srm-YYYYMMDD_HHMMSS`
- Location: Ollama local registry

### 5. Test Your Model

```bash
# List available models
ollama list

# Test inference
ollama run legacy-ai-srm-<timestamp> "Calculate haul rate for 90-minute round trip"

# Interactive mode
python3 legacy_ai.py legacy-ai-srm-<timestamp>
```

---

## Training Pipeline

### Architecture

```
Firestore (Drivers, Plants)
    ↓
training_data_builder.py
    ↓
Instruction-Following Datasets (.jsonl)
    ↓
model_trainer.py
    ↓
Fine-Tuned Llama Model
    ↓
legacy_ai.py (Production Inference)
```

### Dataset Format

Training data uses instruction-following format:

```json
{
  "instruction": "Calculate the haul rate for driver John Doe with a round trip time of 90 minutes.",
  "input": "",
  "output": "For John Doe with 90 minutes round trip:\nRate = ($130 / 60 mins) × 90 / 25 tons = $8.00\nStatus: active",
  "context": "SRM Dispatch - Haul Rate Calculation"
}
```

### Training Methods

#### Method 1: Ollama (Recommended)

**Pros:**
- Simple, no additional dependencies
- Works on CPU
- Fast setup
- Good for most use cases

**Cons:**
- Less control over fine-tuning
- Basic LoRA support

**Command:**
```bash
python3 model_trainer.py
```

#### Method 2: Unsloth (Advanced)

**Pros:**
- 2x faster training
- Full LoRA/QLoRA control
- Better memory efficiency
- Professional-grade results

**Cons:**
- Requires GPU
- More complex setup
- Additional dependencies

**Setup:**
```bash
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

# Train with Unsloth
python3 model_trainer.py --method unsloth
```

---

## Configuration

### training_config.yaml

Edit configuration to customize training:

```yaml
model:
  base_model: "llama3.2"  # or "llama3.2:3b" for larger model

training:
  hyperparameters:
    learning_rate: 2e-4
    max_steps: 500        # Increase for better results
    batch_size: 2

paths:
  model_dir: "/mnt/8tb_drive/legacy_ai/models"
  dataset_dir: "/mnt/8tb_drive/legacy_ai/datasets"
```

### System Prompt

The AI is trained with your custom system prompt (in `training_config.yaml`):

```
You are Legacy AI, Shane Brazelton's personal dispatch optimization assistant.

Your expertise:
- Haul rate calculation: ($130/60) × RTM / 25 tons, rounded to $0.50, min $6.00
- Driver assignment optimization
- Route planning with plant codes

Communication style:
- Direct and concise (no filler, no apologies)
- Data-driven recommendations
- Cite specific driver names and rates
```

---

## Production Deployment

### Option 1: Interactive CLI

```bash
python3 legacy_ai.py legacy-ai-srm-<timestamp>
```

**Commands:**
- `exit` - Save and quit
- `save` - Save conversation
- `context` - Show operational data
- `drivers` - List active drivers

### Option 2: Python API

```python
from legacy_ai import LegacyAI

# Initialize
ai = LegacyAI(model_name="legacy-ai-srm-20260103_120000")
ai.initialize_firebase()

# Query with real-time context
response = ai.query("Which driver should I assign for urgent delivery?")
print(response)

# Get dispatch recommendation
recommendation = ai.get_dispatch_recommendation({
    "weight_tons": 25,
    "destination": "PLANT001",
    "priority": "cost"
})
print(recommendation)
```

### Option 3: Integrate with LogiBot Core

```python
# In logibot_core.py
from legacy_ai import LegacyAI

class LogiBotOrchestrator:
    def __init__(self):
        self.legacy_ai = LegacyAI(model_name="legacy-ai-srm-latest")
        self.legacy_ai.initialize_firebase()

    def get_ai_recommendation(self, query: str):
        return self.legacy_ai.query(query, include_context=True)
```

---

## Continuous Learning

### Automatic Retraining

```bash
# Run once
python3 continuous_learner.py once

# Run continuously (checks every 24 hours)
python3 continuous_learner.py continuous
```

### Schedule with Cron

```bash
# Retrain weekly (Sunday at 2 AM)
0 2 * * 0 cd /path/to/angel-cloud && /path/to/venv/bin/python3 continuous_learner.py once >> logs/training.log 2>&1
```

### Configuration

Edit `training_config.yaml`:

```yaml
continuous_learning:
  enabled: true
  retrain_interval_days: 7    # Retrain weekly
  min_new_examples: 50        # Minimum new data required
  auto_deploy: false          # Manual approval for production
```

---

## Model Management

### List Models

```bash
python3 model_manager.py
```

### Set Active Model

```bash
# In Python
from model_manager import ModelManager

manager = ModelManager()
manager.set_active_model("legacy-ai-srm-20260103_120000")
```

### Cleanup Old Models

```bash
# Keep last 5 versions
from model_manager import ModelManager

manager = ModelManager()
manager.cleanup_old_models(keep_last_n=5)
```

### Export Model

```bash
manager.export_model(
    "legacy-ai-srm-20260103_120000",
    "/backup/models"
)
```

---

## Dataset Details

### Data Sources

1. **Driver Data** (Firestore: `/artifacts/logibot/public/data/drivers`)
   - Name, RTM, haul rate, status
   - Generates 3 training examples per driver

2. **Plant Data** (Firestore: `/artifacts/logibot/public/data/plants`)
   - Plant codes, locations
   - Generates 1 example per plant

3. **Shanebrain Memory** (`ai-mission-statement.md`)
   - System architecture
   - Business logic
   - Communication protocol

4. **Decision Patterns** (Historical data)
   - Driver assignment decisions
   - Cost vs. speed tradeoffs
   - Optimization strategies

### Example Counts

For 19 active drivers + 10 plants:
- Driver examples: 57 (19 × 3)
- Plant examples: 10
- Memory examples: ~20
- Decision examples: ~15
- **Total: ~100 base examples**

With augmentation (2x variations): **~200 training examples**

---

## Monitoring & Evaluation

### Test Queries

```bash
ollama run legacy-ai-srm-<timestamp>

# Test calculations
"Calculate the haul rate for a 90-minute round trip."

# Test recommendations
"Which driver has the lowest cost?"
"Assign a driver for urgent delivery."

# Test knowledge
"What is the haul rate formula?"
"Who is Shane Brazelton?"
```

### Expected Behavior

✅ **MUST:**
- Cite haul rate formula correctly
- Recommend specific driver names from active roster
- Consider both cost and availability
- Use direct communication (no apologies/filler)

❌ **MUST NOT:**
- Hallucinate driver names
- Ignore operational context
- Use verbose/apologetic language

### Metrics

Track in model metadata:
- Training examples count
- Training time
- Dataset version
- Base model version

---

## Troubleshooting

### Ollama Not Found

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Verify
ollama --version
```

### 8TB Drive Not Mounted

```bash
# Check mount
df -h | grep 8tb

# Remount
sudo mount /dev/sdX1 /mnt/8tb_drive
```

### Out of Memory During Training

**Solutions:**
1. Use smaller base model: `llama3.2:1b`
2. Reduce batch size in `training_config.yaml`
3. Enable swap:
```bash
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Training Takes Too Long

**Optimizations:**
1. Use GPU if available
2. Reduce `max_steps` in config
3. Use Unsloth for 2x speedup
4. Train on subset of data initially

### Model Not Learning

**Debugging:**
1. Check dataset quality:
```bash
head -5 /mnt/8tb_drive/legacy_ai/datasets/legacy_ai_complete_train_*.jsonl
```

2. Verify examples are varied
3. Increase `max_steps` (try 1000+)
4. Check system prompt relevance

---

## Advanced Topics

### Custom System Prompts

Edit `training_config.yaml`:

```yaml
system_prompt: |
  You are Legacy AI, specialized in [YOUR USE CASE].

  Your expertise:
  - [LIST YOUR DOMAIN KNOWLEDGE]

  Communication style:
  - [DEFINE YOUR PREFERRED STYLE]
```

### Multi-Model Strategy

Train specialized models:

```bash
# Cost optimization specialist
python3 model_trainer.py --focus=cost_optimization

# Speed optimization specialist
python3 model_trainer.py --focus=speed_optimization

# General dispatcher
python3 model_trainer.py --focus=general
```

### Integration with External Tools

```python
# Route planning with Google Maps API
def enhanced_recommendation(ai, load_details):
    # Get AI recommendation
    recommendation = ai.get_dispatch_recommendation(load_details)

    # Enhance with real-time traffic
    traffic_data = get_traffic_data(load_details['destination'])

    return f"{recommendation}\n\nReal-time traffic: {traffic_data}"
```

---

## Storage Layout

```
/mnt/8tb_drive/legacy_ai/
├── datasets/
│   ├── dispatch_optimization_20260103_120000.jsonl
│   ├── shanebrain_memory_20260103_120000.jsonl
│   ├── decision_patterns_20260103_120000.jsonl
│   ├── legacy_ai_complete_20260103_120000.jsonl
│   ├── legacy_ai_complete_train_20260103_120000.jsonl
│   ├── legacy_ai_complete_val_20260103_120000.jsonl
│   └── metadata.json
├── models/
│   ├── legacy-ai-srm-20260103_120000_Modelfile
│   ├── legacy-ai-srm-20260103_120000_metadata.json
│   └── model_registry.json
├── memory/
│   ├── session_20260103_120000.json
│   └── session_20260103_150000.json
└── cache/
    └── ollama_cache/
```

---

## Performance Benchmarks

### Training (Ollama Method)
- **CPU (8-core)**: 10-15 minutes
- **GPU (8GB VRAM)**: 5-8 minutes

### Inference
- **First Token**: 500-800ms
- **Tokens/sec**: 15-25 (CPU), 40-60 (GPU)

### Storage
- **Base Model**: 1-2 GB
- **Fine-Tuned Model**: +200-500 MB
- **Datasets**: 1-5 MB
- **Memory (1 year)**: ~100 MB

---

## Best Practices

1. **Data Quality Over Quantity**
   - 100 high-quality examples > 1000 poor examples
   - Ensure examples reflect actual operations

2. **Regular Retraining**
   - Weekly retraining captures new patterns
   - Keep models current with operational changes

3. **Version Control**
   - Keep last 5 model versions
   - Tag models with metadata
   - Test before deploying to production

4. **Monitor Performance**
   - Test with validation queries
   - Track response quality
   - Collect user feedback

5. **Backup Strategy**
   - Export models monthly
   - Backup datasets to cloud
   - Version control Modelfiles

---

## Cost Analysis

### Fixed Costs (One-Time)
- 8TB External Drive: $150-200
- Hardware (if upgrading): $0-1000

### Ongoing Costs
- **Cloud Alternative**: $1,000/month
- **Legacy AI**: $0/month
- **ROI**: Pays for itself in < 1 month

### Resource Usage
- Disk: 10-20 GB (8TB drive)
- Power: ~50W during training
- Bandwidth: 0 (fully local)

---

**Last Updated:** 2026-01-03
**Version:** 1.0
**Maintainer:** Shane Brazelton

**Mission:** Replace $1,000/mo cloud AI costs with self-hosted intelligence.
