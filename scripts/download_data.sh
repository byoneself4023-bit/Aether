#!/bin/bash

echo "Downloading data from AI Hub..."

DATA_DIR="./data/raw"

# Create directories
mkdir -p $DATA_DIR/korean_dialogue
mkdir -p $DATA_DIR/callcenter_qa
mkdir -p $DATA_DIR/llm_instruction

echo "Please download data manually from AI Hub:"
echo "1. 한국어 대화 데이터: https://aihub.or.kr/"
echo "2. 콜센터 QA 데이터: https://aihub.or.kr/"
echo "3. LLM 인스트럭션 데이터: https://aihub.or.kr/"

echo ""
echo "Place downloaded files in:"
echo "- $DATA_DIR/korean_dialogue/"
echo "- $DATA_DIR/callcenter_qa/"
echo "- $DATA_DIR/llm_instruction/"

echo "Data directories prepared!"
