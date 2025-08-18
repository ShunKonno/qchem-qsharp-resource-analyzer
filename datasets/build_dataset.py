#!/usr/bin/env python3
"""
CLI本体（再実行/レジューム対応）
データセット生成のメインスクリプト
"""

import argparse
import yaml
import logging
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Build dataset for QChem-QSharp resource analysis")
    parser.add_argument("--config", type=str, default="config.yaml", help="Configuration file")
    parser.add_argument("--resume", action="store_true", help="Resume from previous run")
    parser.add_argument("--output", type=str, default="data/processed", help="Output directory")
    
    args = parser.parse_args()
    
    # Load configuration
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"Building dataset with config: {config}")
    print(f"Resume mode: {args.resume}")
    print(f"Output directory: {args.output}")
    
    # TODO: Implement dataset building logic
    print("Dataset building completed!")

if __name__ == "__main__":
    main()
