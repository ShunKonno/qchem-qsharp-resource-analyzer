
# 小分子量子化学計算のための量子リソースランドスケープ (Q\# × Python)

量子計算が真にブレイクスルーを起こすのは、強相関・励起を含む厳密な電子構造を現実的コストで扱える点であるが、必要な量子リソース（Tゲート数・論理/物理量子ビット・回路深さ・実行時間）がボトルネックで、分子/設定ごとに“どこまで実行可能か”の見通しが課題です。
本プロジェクトは化学精度は評価せず、量子リソース指標のみに特化して高速予測・分析を行うことで、

-　「どの活性空間なら実行可能か」を即時に可視化
-　大量・多設定の探索で“粗→精”の振り分けを自動化
-　ハードウェア/アルゴリズム設計や実験計画の意思決定を高速化

を実現します。
***

The true breakthrough of quantum computing lies in its ability to handle exact electronic structures, including strong correlations and excitations, at a realistic cost. However, the required quantum resources—such as the number of T-gates, logical/physical qubits, circuit depth, and execution time—present a significant bottleneck. A key challenge is predicting the feasibility of these calculations for each specific molecule and configuration.

This project focuses exclusively on the high-speed prediction and analysis of quantum resource metrics, without evaluating chemical accuracy. By doing so, it aims to:

-   Instantly visualize **which active spaces are feasible** for a given quantum computation.
-   Automate a **"coarse-to-fine" screening process** across a vast number of molecules and settings.
-   Accelerate decision-making in **hardware/algorithm design and experimental planning**.
-----

## スコープ
- 入力
	 1.	分子グラフ（原子種・結合・荷電・芳香性などの軽量属性）
	 2.	計算設定：基底関数、エンコーディング（JW/BK）、分解法（Trotter/低ランク/…）、活性空間 CAS(nₑ,nₒ)、誤り訂正前提（物理誤り率・コード距離方針・サイクルタイム・工場ポリシー 等）
-	出力（予測ターゲット）
T_count, logical_qubits, circuit_depth, wall_time_s（必要に応じ physical_qubits, code_distance, factories など派生量も）
-	対象系
小〜中分子、金属錯体、イオン、高分子（〜1000原子規模まで）。活性空間は CAS(2,2)〜CAS(30,30) を主レンジ。
-----

## 開発環境

このプロジェクトは **Docker + conda 環境** 上で開発を行います。  
QuTiP, PySCF は conda 管理、qsharp は pip により補完インストールしています。

### 環境構成
- **base環境**: 最小限のconda環境（用途未定、将来の拡張用）
- **qchem-qsharp-ds環境**: 開発用のメイン環境（PySCF, qsharp等を含む）

-----

## 起動手順

### 1. Docker イメージのビルド
プロジェクトルートで以下を実行してください。

```bash
docker build -f docker/Dockerfile -t qchem-dev:conda .
```

### 2. コンテナを起動してシェルに入る

開発用の対話シェルを起動する場合:

```bash
docker run --rm -it -v "$PWD":/workspace qchem-dev:conda bash
```

- `-v "$PWD":/workspace`: 現在のホストディレクトリを `/workspace` にマウント
- 起動後は自動で `qchem-qsharp-ds` 環境が有効化されます

### 3. ワンショットでコマンド実行

Python のバージョン確認:

```bash
docker run --rm qchem-dev:conda python -V
```

ライブラリの動作確認:

```bash
docker run --rm qchem-dev:conda python - <<'PY'
import qutip, pyscf, qsharp
print("QuTiP:", qutip.__version__)
print("PySCF:", pyscf.__version__)
print("qsharp import OK")
PY
```

### 4. コンテナを残して開発する場合

開発を継続したい場合は名前付きコンテナを起動します。

```bash
docker run -it --name qchem-dev -v "$PWD":/workspace qchem-dev:conda bash
```

終了後も再開可能です:

```bash
docker start -ai qchem-dev
```

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

  - Docker
  - 上記の起動手順でDockerイメージをビルド済み

### 1\) セットアップ (Docker + conda)

```bash
# Dockerイメージのビルド
docker build -f docker/Dockerfile -t qchem-dev:conda .

# コンテナを起動してシェルに入る
docker run --rm -it -v "$PWD":/workspace qchem-dev:conda bash
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
├─ docker/                      # Docker設定ファイル
│  └─ Dockerfile               # 開発環境用Dockerfile
├─ qsharp/                      # Q# リソース推定ドライバ
├─ scripts/                     # Python パイプラインスクリプト
├─ config/                      # パラメータグリッド
├─ inputs/                      # 分子入力ファイル
├─ intermediate/                # 中間フォーマット
├─ data/                        # 出力データセット
├─ notebooks/                   # 解析用ノートブック
├─ env/                         # 環境ファイル
│  ├─ environment.yml          # conda環境設定
│  └─ requirements.txt         # pip依存関係（フォールバック用）
└─ README.md
```

-----

## ロードマップ

  - **v1.0**: STO-3G / 6-31G, JW + Trotter, 化学精度グリッド, 推奨機能
  - **v1.1**: BKエンコーディング, 活性空間のバリエーション, 不確実性解析
  - **v1.2**: Qubitizationパス, $ \\lambda $プロキシ特徴量, Streamlit UI

-----

## トラブルシューティング

### condaの利用規約エラー
```bash
# コンテナ内で以下を実行
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```

### qsharpのインポートエラー
`env/requirements.txt`のフォールバック版を使用してください：
```bash
# qsharp関連の行をコメントアウト
sed -i 's/^qsharp/# qsharp/' env/requirements.txt
sed -i 's/^qsharp-chemistry/# qsharp-chemistry/' env/requirements.txt

# Dockerイメージを再ビルド
docker build -f docker/Dockerfile -t qchem-dev:conda .
```

-----

## 参考文献

  - **Q\# Chemistry & Broombridge**: [https://arxiv.org/abs/1904.01131](https://arxiv.org/abs/1904.01131)
  - **Resource Estimator (Chemistry tutorial)**: [https://learn.microsoft.com/en-us/azure/quantum/tutorial-resource-estimator-chemistry](https://learn.microsoft.com/en-us/azure/quantum/tutorial-resource-estimator-chemistry)
  - **Q\# Overview**: [https://learn.microsoft.com/en-us/azure/quantum/qsharp-overview](https://learn.microsoft.com/en-us/azure/quantum/qsharp-overview)