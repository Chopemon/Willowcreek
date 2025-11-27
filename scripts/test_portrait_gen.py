#!/usr/bin/env python3
"""
Test script for portrait generation

This script helps you test your API setup before generating all portraits.
It will generate just one test portrait to verify everything works.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_portraits import PortraitGenerator


def test_api(api_type: str, api_key: str = None):
    """Test a specific API with a single character"""

    print(f"\n{'='*60}")
    print(f"🧪 Testing {api_type.upper()} API")
    print(f"{'='*60}\n")

    # Create test generator
    generator = PortraitGenerator(api_type, api_key)

    # Test with Sarah Madison (first character in roster)
    test_character = "Sarah Madison"
    test_prompt = generator.prompts["npc_roster"][test_character]

    print(f"📝 Test Character: {test_character}")
    print(f"📝 Prompt Preview: {test_prompt[:100]}...\n")

    # Generate
    success = generator.generate_portrait(test_character, test_prompt, "test")

    if success:
        print(f"\n✅ SUCCESS! API is working correctly.")
        print(f"📁 Check: portraits/test/{test_character.replace(' ', '_')}.png")
        print(f"\n💡 You can now generate all portraits with:")
        print(f"   python scripts/generate_portraits.py --api {api_type} --category all\n")
        return True
    else:
        print(f"\n❌ FAILED! Check the error messages above.")
        print(f"\n💡 Common issues:")
        print(f"   - Invalid or missing API key")
        print(f"   - API library not installed (run: pip install {api_type})")
        print(f"   - Network connectivity issues")
        print(f"   - Rate limiting\n")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Test portrait generation API setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/test_portrait_gen.py --api openai
  python scripts/test_portrait_gen.py --api stability --api-key "sk-..."
  python scripts/test_portrait_gen.py --api local
        """
    )

    parser.add_argument(
        "--api",
        type=str,
        required=True,
        choices=["openai", "stability", "replicate", "local"],
        help="Which API to test"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="API key (or set via environment variable)"
    )

    args = parser.parse_args()

    # Run test
    success = test_api(args.api, args.api_key)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
