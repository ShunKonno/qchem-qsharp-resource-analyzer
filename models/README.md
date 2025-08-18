# Models Directory

このディレクトリには学習済みのモデル重みファイル（*.pt）が保存されます。

## ファイル形式

- `best_model.pt`: 検証セットで最高性能を示したモデル
- `latest_model.pt`: 最新の学習済みモデル
- `checkpoint_epoch_N.pt`: エポックNでのチェックポイント

## 使用方法

```python
import torch
from models import YourModel

# モデルの定義
model = YourModel()

# 学習済み重みの読み込み
checkpoint = torch.load('models/best_model.pt')
model.load_state_dict(checkpoint['model_state_dict'])

# 推論モードに設定
model.eval()
```

## 注意事項

- モデルファイルはGitで管理しない（.gitignoreに追加）
- 大きなファイルの場合は外部ストレージの使用を検討
- モデルのバージョン管理は別途実施
