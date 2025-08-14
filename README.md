# 小分子量子化学計算のための量子リソースランドスケープ (Q\# × Python)

**要約 (TL;DR)** このリポジトリは、様々な設定（基底関数系、活性空間、エンコーディング、分解手法、目標化学精度、誤り訂正）の下で、小分子の量子化学計算に必要な量子リソース（論理量子ビット数、Tゲート数、回路深度、実行時間）を推定します。  
再現可能なパイプライン（PySCF/NWChem → Broombridge → Q\# Resource Estimator → CSV）と、指定された化学精度を満たす**最小コストの計算設定**を提案するリコメンダー機能を提供します。

-----

## 本リポジトリの意義

  - 分子問題の量子計算コストは、**基底関数系、活性空間、エンコーディング、分解手法、エラーの仮定**によって大きく変動します。
  - このツールキットは、これらの変数を体系的に調査し、**リソースランドスケープ**を生成します。
  - これにより、研究者や意思決定者は、**将来のフォールトトレラント量子デバイスで実行可能な計算設定**を評価することができます。

-----

## パイプライン概要

入力 (SMILES/XYZ)
→ 古典計算による積分 (PySCF/NWChem)
→ Broombridge (QDK化学フォーマット)
→ Q\# リソース推定器 (設定グリッド)
→ `resource_estimates.csv`
→ 解析 / 可視化 / 推奨

-----

## クイックスタート

### 0\) 前提条件

  - Python 3.10+
  - Microsoft Quantum Development Kit (Q\#)
  - PySCF または NWChem (少なくともいずれか一方)

### 1\) セットアップ (conda)

```bash
conda env create -f env/environment.yml
conda activate qchem-qsharp-ds
```

### 2\) 分子データの準備

XYZファイルを `inputs/xyz/` に配置するか、SMILES文字列を `inputs/smiles.txt` にリストアップします。

### 3\) Broombridgeへの変換

```bash
python scripts/convert_to_broombridge.py \
  --xyz inputs/xyz \
  --out intermediate/broombridge
```

### 4\) バッチリソース推定

```bash
python scripts/batch_run.py \
  --grid config/grid.yml \
  --broombridge intermediate/broombridge \
  --out data/resource_estimates.csv \
  --n-proc 8 --resume
```

### 5\) 結果の探索と推奨

```bash
jupyter lab  # notebooks/analysis.ipynb を開く
```

またはCLIで実行:

```bash
python scripts/recommend.py --molecule "H2O" --objective Min-T --chem-acc 1.6
```

-----

## 設定ファイルの例 (`config/grid.yml`)

```yaml
basis: ["STO-3G", "6-31G"]
active_space: ["full", "homo±1"]
encoding: ["JW"]
decomposition: ["Trotter"]
target_error_mHa: [0.8, 1.6, 2.0]
phys_error_rate: [1.0e-3, 1.0e-4] # 物理エラー率 ($10^{-3}$, $10^{-4}$)
molecules: "inputs/xyz/*.xyz"
```

-----

## 出力スキーマ (`data/resource_estimates.csv`)

  - **分子メタデータ**: ID, SMILES, 化学式, 原子数, 電子数
  - **計算設定**: 基底関数系, 活性軌道, エンコーディング, 分解手法, 目標誤差
  - **リソース推定値**: 論理量子ビット数, Tゲート数, 回路深度, 実行時間
  - **実行情報**: ID, タイムスタンプ

-----

## リポジトリ構造

```
qchem-qsharp-resource-landscape/
├─ qsharp/                      # Q# リソース推定ドライバ
├─ scripts/                     # Python パイプラインスクリプト
├─ config/                      # パラメータグリッド
├─ inputs/                      # 分子入力ファイル
├─ intermediate/                # 中間フォーマット
├─ data/                        # 出力データセット
├─ notebooks/                   # 解析用ノートブック
├─ env/                         # 環境ファイル
└─ README.md
```

-----

## ロードマップ

  - **v1.0**: STO-3G / 6-31G, JW + Trotter, 化学精度グリッド, 推奨機能
  - **v1.1**: BKエンコーディング, 活性空間のバリエーション, 不確実性解析
  - **v1.2**: Qubitizationパス, $ \\lambda $プロキシ特徴量, Streamlit UI

-----

## 参考文献

  - **Q\# Chemistry & Broombridge**: [https://arxiv.org/abs/1904.01131](https://arxiv.org/abs/1904.01131)
  - **Resource Estimator (Chemistry tutorial)**: [https://learn.microsoft.com/en-us/azure/quantum/tutorial-resource-estimator-chemistry](https://learn.microsoft.com/en-us/azure/quantum/tutorial-resource-estimator-chemistry)
  - **Q\# Overview**: [https://learn.microsoft.com/en-us/azure/quantum/qsharp-overview](https://learn.microsoft.com/en-us/azure/quantum/qsharp-overview)