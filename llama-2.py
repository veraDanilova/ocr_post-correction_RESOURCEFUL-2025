"""
Re-used script from:
https://github.com/Shef-AIRE/llms_post-ocr_correction/blob/main/llama-2.py
with the German prompt (translation of the original English prompt) and models

"""

from datasets import Dataset
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer
import argparse
import os
import pandas as pd
import torch
import yaml


# Load Llama 2 config from YAML file
def load_config(file):
    with open(file, 'r') as f:
        config = yaml.safe_load(f)
    return config['llama-2']

# Formats sample into prompt template
def prompt_template(example):
    return f"""### Anweisung:
Korrigieren Sie die OCR-Fehler im bereitgestellten Text.

### Eingabe:
{example['OCR Text']}

### Antwort:
{example['Ground Truth']}
"""

# Main function for instruction-tuning Llama 2
def main(args):
    # Load config
    config = load_config(args.config)

    # Select model
    model_name = f'{args.model.capitalize()}'
    output_dir = os.path.join('model', f'{os.path.basename(args.model)}-ocr')

    # Set up training data
    train = pd.read_csv(args.data)
    train = train.query("Publication in ['Diabetiker_journal', 'Neue_Zürcher_Zeitung(NZZ)']")
    train = Dataset.from_pandas(train)

    # Quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type='nf4',
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    # LoRA config
    peft_config = LoraConfig(
        lora_alpha=16,
        lora_dropout=0.1,
        r=64,
        bias='none',
        task_type='CAUSAL_LM',
    )

    # Initialise Llama 2
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        use_cache=False,
        device_map='auto',
    )
    model.config.pretraining_tp = 1
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, peft_config)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = 'right'

    # Instruction-tune Llama 2
    config['learning_rate'] = float(config['learning_rate'])
    train_args = SFTConfig(
        output_dir=output_dir,
        **config,
    )
    trainer = SFTTrainer(
        model=model,
        args=train_args,
        train_dataset=train,
        peft_config=peft_config,
        max_seq_length=1024,
        tokenizer=tokenizer,
        packing=True,
        formatting_func=prompt_template,
    )
    trainer.train()
    trainer.save_model(output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Instruction-tuning German Llama')
    parser.add_argument('--model', type=str, choices=['jphme/em_german_13b_v01', 'jphme/em_german_70b_v01', 'jphme/em_german_leo_mistral','PleIAs/OCRonos'], 
                        default='jphme/em_german_13b_v01')
    parser.add_argument('--config', type=str, help='Path to config')
    parser.add_argument('--data', type=str, help='Path to training data')
    args = parser.parse_args()
    main(args)