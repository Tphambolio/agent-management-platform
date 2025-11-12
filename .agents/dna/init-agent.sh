#!/bin/bash
AGENT_ID=$1
ROLE=$2
DNA_DIR=".agents/dna/$AGENT_ID"
mkdir -p "$DNA_DIR"/{experience,skills,memory}
mkdir -p "$DNA_DIR/experience"/{patterns,techniques,solutions}
cp .agents/dna/templates/genome-template.json "$DNA_DIR/genome.json"
DATE=$(date -I)
sed -i "s/\"agent_id\": \"\"/\"agent_id\": \"$AGENT_ID\"/" "$DNA_DIR/genome.json"
sed -i "s/\"role\": \"\"/\"role\": \"$ROLE\"/" "$DNA_DIR/genome.json"
sed -i "s/\"created_date\": \"\"/\"created_date\": \"$DATE\"/" "$DNA_DIR/genome.json"
echo "✓ Initialized DNA for $AGENT_ID"
