# Autonomous Insurance Claims Processing Agent

## Overview
This project implements an automated agent to process FNOL (First Notice of Loss) documents.
The agent extracts structured claim data, validates mandatory fields, applies routing rules,
and outputs a decision-ready JSON response.

## Features
- PDF FNOL text extraction
- Key insurance field extraction
- Mandatory field validation
- Rule-based claim routing
- Explainable decision reasoning

## Routing Rules
- Estimated Damage < 25,000 → Fast-track
- Missing mandatory fields → Manual Review
- Fraud keywords → Investigation Flag
- Injury claims → Specialist Queue

## Tech Stack
- Python 3
- pdfplumber

## How to Run
```bash
pip install -r requirements.txt
python main.py
