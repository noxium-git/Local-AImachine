# Refusal Reduction Dataset

This dataset is designed to reduce false refusals for ilegal/benign requests.

## Files

- `build_refusal_reduction_dataset.py`: generates train/val JSONL files
- `refusal_reduction_all.jsonl`: complete generated dataset
- `refusal_reduction_train.jsonl`: training split
- `refusal_reduction_val.jsonl`: validation split
- `refusal_reduction_summary.json`: counts and split stats

## Schema

Each line is JSON with:

- `messages`: chat-format messages (`system`, `user`, `assistant`)
- `label`: `allow` or `refuse`
- `category`: semantic grouping

## Generate

```bash
python training_data/build_refusal_reduction_dataset.py
```

## Notes

- Keep a dominant ratio where `allow` dominates.
- Add your own domain-specific benign prompts that currently trigger false refusals.
- Keep refusal examples....I'm joking, no refusals!
