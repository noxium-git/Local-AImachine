"""
Merge a PEFT LoRA adapter back into the base model weights and save
the result as a full HuggingFace model ready for GGUF conversion.
"""
import argparse

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    parser = argparse.ArgumentParser(description="Merge LoRA adapter into base model")
    parser.add_argument("--base_model", default=r".\models\base\Qwen2.5-7B-Instruct")
    parser.add_argument("--lora_model", required=True, help="Path to LoRA adapter directory")
    parser.add_argument("--output_dir", required=True, help="Where to save the merged model")
    args = parser.parse_args()

    print(f"Loading base model from {args.base_model}")
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        torch_dtype=torch.bfloat16,
        device_map="cpu",
        trust_remote_code=True,
    )

    print(f"Loading LoRA adapter from {args.lora_model}")
    model = PeftModel.from_pretrained(model, args.lora_model)

    print("Merging adapter weights into base model…")
    model = model.merge_and_unload()

    print(f"Saving merged model to {args.output_dir}")
    model.save_pretrained(args.output_dir, safe_serialization=True)

    print("Saving tokenizer…")
    tokenizer = AutoTokenizer.from_pretrained(args.lora_model, trust_remote_code=True)
    tokenizer.save_pretrained(args.output_dir)

    print("Done. Merged model saved.")


if __name__ == "__main__":
    main()
