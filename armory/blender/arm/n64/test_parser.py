"""
Standalone test script for trait parsing.
Run this directly with Python (outside Blender).
"""
from trait_parser import parse_trait, print_trait


if __name__ == '__main__':
    # Test with Level.hx
    print("Testing Level.hx:")
    trait = parse_trait(r'd:\Game Development\Armory\n64\first_test\Sources\arm\Level.hx')
    print_trait(trait)

    # Test with Rotator.hx
    print("\nTesting Rotator.hx:")
    trait = parse_trait(r'd:\Game Development\Armory\n64\first_test\Sources\arm\Rotator.hx')
    print_trait(trait)
