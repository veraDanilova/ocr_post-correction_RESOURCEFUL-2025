# Post-OCR Correction of Historical German Periodicals using LLMs

This repository contains the scripts used for the paper **"Post-OCR Correction of Historical German Periodicals using LLMs"** (Danilova & Aangenendt, 2025), accepted at the RESOURCEFUL workshop of NoDaLiDa-2025. The csv files with the evaluation results will be uploaded here soon.

## Project Structure

### Main Files

- `prepare_dataset.ipynb`: Prepares the dataset for post-OCR correction. It downloads the data, preprocesses it, aligns the OCR text with the ground truth text, calculates the character error rate (CER), prepares train-test split
- `llama-2.py`: Fine-tunes the Llama 2 model for OCR correction using the prepared dataset (re-used).
- `bart.py`: Fine-tunes the BART model for OCR correction using the prepared dataset (re-used).
- `results.ipynb`: Evaluates the performance of the models and calculates the CER reduction.
- `analyze_inference.ipynb`: Analyzes the inference results and calculates various metrics.

## License

This project is licensed under the terms of the MIT license.