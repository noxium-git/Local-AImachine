"""
LoRA SFT training script for Court refusal-reduction fine-tuning.
Uses TRL SFTTrainer with PEFT LoRA on a chat-format JSONL dataset.
"""
import argparse
import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, TaskType
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer


def load_jsonl(path: str) -> Dataset:
    import re
    # Valid JSON escape chars: " \ / b f n r t u
    _bad_escape = re.compile(r'\\([^"\\/bfnrtu0-9])')
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                # Replace invalid escapes (e.g. \$) with the bare character
                line = _bad_escape.sub(r'\1', line)
                rows.append(json.loads(line))
    return Dataset.from_list(rows)


def format_messages(example, tokenizer):
    """Apply the model's chat template to the messages list."""
    text = tokenizer.apply_chat_template(
        example["messages"],
        tokenize=False,
        add_generation_prompt=False,
    )
    return {"text": text}


def main():
    parser = argparse.ArgumentParser(description="LoRA SFT trainer")
    parser.add_argument("--base_model", default=r".\models\base\Qwen2.5-7B-Instruct")
    parser.add_argument("--train_file", required=True)
    parser.add_argument("--val_file", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--per_device_train_batch_size", type=int, default=2)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=8)
    parser.add_argument("--learning_rate", type=float, default=2e-4)
    parser.add_argument("--num_train_epochs", type=int, default=3)
    parser.add_argument("--max_seq_length", type=int, default=2048)
    parser.add_argument("--lora_r", type=int, default=16)
    parser.add_argument("--lora_alpha", type=int, default=32)
    parser.add_argument("--lora_dropout", type=float, default=0.05)
    args = parser.parse_args()

    print(f"Loading tokenizer from {args.base_model}")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.model_max_length = args.max_seq_length
    tokenizer.truncation_side = "right"

    print("Loading training data")
    train_ds = load_jsonl(args.train_file)
    val_ds = load_jsonl(args.val_file)

    train_ds = train_ds.map(lambda ex: format_messages(ex, tokenizer))
    val_ds = val_ds.map(lambda ex: format_messages(ex, tokenizer))

    use_4bit = torch.cuda.is_available()
    bnb_config = None
    if use_4bit:
        print("CUDA available — using 4-bit quantization (QLoRA)")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
    else:
        print("No CUDA detected — loading in fp32 (CPU training, will be slow)")

    print(f"Loading base model from {args.base_model}")
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        quantization_config=bnb_config,
        device_map="auto" if use_4bit else None,
        trust_remote_code=True,
        dtype=torch.bfloat16 if not use_4bit else None,
    )
    model.config.use_cache = False

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        bias="none",
    )

    sft_config = SFTConfig(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.per_device_train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        num_train_epochs=args.num_train_epochs,
        dataset_text_field="text",
        logging_steps=10,
        save_strategy="epoch",
        eval_strategy="epoch",
        load_best_model_at_end=True,
        bf16=torch.cuda.is_available(),
        warmup_steps=10,
        lr_scheduler_type="cosine",
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        peft_config=lora_config,
    )

    print("Starting training…")
    trainer.train()

    print(f"Saving LoRA adapter to {args.output_dir}")
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print("Done.")


if __name__ == "__main__":
    main()
