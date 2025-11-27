#!/bin/bash
# Convenience script to generate all portraits
# Usage: ./generate_all_portraits.sh [api_type]
# Example: ./generate_all_portraits.sh openai

API_TYPE=${1:-openai}

echo "🎨 Generating all portraits using $API_TYPE..."
echo ""

# Check if API key is set
if [ "$API_TYPE" = "openai" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set!"
    echo "   Run: export OPENAI_API_KEY=\"sk-...\""
    exit 1
fi

if [ "$API_TYPE" = "stability" ] && [ -z "$STABILITY_API_KEY" ]; then
    echo "❌ STABILITY_API_KEY not set!"
    echo "   Run: export STABILITY_API_KEY=\"sk-...\""
    exit 1
fi

if [ "$API_TYPE" = "replicate" ] && [ -z "$REPLICATE_API_KEY" ]; then
    echo "❌ REPLICATE_API_KEY not set!"
    echo "   Run: export REPLICATE_API_KEY=\"r8_...\""
    exit 1
fi

# Generate
python scripts/generate_portraits.py --api "$API_TYPE" --category all

echo ""
echo "✅ Done! Check the portraits/ directory"
