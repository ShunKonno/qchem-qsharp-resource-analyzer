# Data Directory

このディレクトリには、QChem-QSharp resource analysisで使用するデータが保存されます。

## ディレクトリ構造

```
data/
├── raw/              # 生データ（分子ファイル、QChem出力等）
├── intermediate/     # 中間処理データ
├── processed/        # 前処理済みデータ
├── features/         # 特徴量データ
├── cache/           # キャッシュファイル
└── checkpoints/     # チェックポイントファイル
```

## データの種類

### Raw Data
- 分子構造ファイル（.xyz, .mol等）
- QChem計算出力ファイル
- FCIDUMPファイル
- Broombridgeファイル

### Intermediate Data
- 前処理中の一時データ
- 部分的な計算結果

### Processed Data
- 機械学習用に前処理済みのデータ
- 正規化・標準化済みのデータ

### Features
- 分子の特徴量ベクトル
- GNN用のグラフデータ

## 注意事項

- このディレクトリは.gitignoreに追加されている
- 大きなデータファイルは外部ストレージの使用を検討
- データのバックアップを定期的に実施
