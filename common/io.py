"""
CSV/ログ/キャッシュ/レジューム
入出力、ログ、キャッシュ、レジューム機能を提供するモジュール
"""

import csv
import json
import logging
import pickle
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class IOManager:
    """入出力、ログ、キャッシュ、レジュームを管理するクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.io_config = config.get('io', {})
        self.setup_logging()
    
    def setup_logging(self):
        """ログ設定の初期化"""
        log_level = self.io_config.get('log_level', 'INFO')
        log_file = self.io_config.get('log_file', 'app.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def save_csv(self, data: List[Dict[str, Any]], filepath: str):
        """CSVファイルへの保存"""
        if not data:
            return
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        self.logger.info(f"Saved CSV to {filepath}")
    
    def load_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """CSVファイルからの読み込み"""
        data = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        self.logger.info(f"Loaded CSV from {filepath}")
        return data
    
    def save_cache(self, data: Any, cache_key: str):
        """キャッシュへの保存"""
        cache_dir = Path(self.io_config.get('cache_dir', 'data/cache'))
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        cache_file = cache_dir / f"{cache_key}.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
        
        self.logger.info(f"Saved cache: {cache_key}")
    
    def load_cache(self, cache_key: str) -> Optional[Any]:
        """キャッシュからの読み込み"""
        cache_dir = Path(self.io_config.get('cache_dir', 'data/cache'))
        cache_file = cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            self.logger.info(f"Loaded cache: {cache_key}")
            return data
        
        return None
    
    def save_checkpoint(self, data: Dict[str, Any], checkpoint_name: str):
        """チェックポイントの保存（レジューム用）"""
        checkpoint_dir = Path(self.io_config.get('checkpoint_dir', 'data/checkpoints'))
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint_file = checkpoint_dir / f"{checkpoint_name}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Saved checkpoint: {checkpoint_name}")
    
    def load_checkpoint(self, checkpoint_name: str) -> Optional[Dict[str, Any]]:
        """チェックポイントの読み込み（レジューム用）"""
        checkpoint_dir = Path(self.io_config.get('checkpoint_dir', 'data/checkpoints'))
        checkpoint_file = checkpoint_dir / f"{checkpoint_name}.json"
        
        if checkpoint_file.exists():
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
            self.logger.info(f"Loaded checkpoint: {checkpoint_name}")
            return data
        
        return None

def main():
    """テスト用のメイン関数"""
    config = {
        "io": {
            "log_level": "INFO",
            "log_file": "test.log",
            "cache_dir": "data/cache",
            "checkpoint_dir": "data/checkpoints"
        }
    }
    
    io_manager = IOManager(config)
    
    # テスト実行
    test_data = [{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]
    io_manager.save_csv(test_data, "test.csv")
    loaded_data = io_manager.load_csv("test.csv")
    
    print(f"Loaded data: {loaded_data}")

if __name__ == "__main__":
    main()
