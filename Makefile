.PHONY: convert batch recommend smoke test clean help

# Default target
help:
	@echo "QChem Q# Resource Analyzer - Available targets:"
	@echo ""
	@echo "  convert    - Convert SMILES to Broombridge files"
	@echo "  batch      - Run batch resource estimation"
	@echo "  recommend  - Get recommendations for optimal settings"
	@echo "  smoke      - Run full pipeline (convert + batch + recommend)"
	@echo "  test       - Run all tests"
	@echo "  clean      - Clean generated files"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make convert"
	@echo "  make batch"
	@echo "  make recommend"
	@echo "  make smoke"

# Convert SMILES to Broombridge
convert:
	@echo "🔄 Converting SMILES to Broombridge files..."
	python scripts/convert_to_broombridge.py --smiles-list config/molecules.list --out intermediate/broombridge --verbose

# Run batch resource estimation
batch:
	@echo "🚀 Running batch resource estimation..."
	python scripts/batch_run.py --grid config/grid.yml --broombridge intermediate/broombridge --out data/resource_estimates.csv --smiles-list config/molecules.list --n-proc 4 --resume

# Get recommendations
recommend:
	@echo "💡 Getting recommendations for H2O (Min-T, chem acc ≤ 1.6 mHa)..."
	python scripts/recommend.py --molecule H2O --objective Min-T --chem-acc 1.6 --verbose

# Run full pipeline
smoke: convert batch recommend
	@echo ""
	@echo "🎉 Full pipeline completed successfully!"
	@echo "📊 Results available in: data/resource_estimates.csv"
	@echo "📁 Broombridge files in: intermediate/broombridge/"
	@echo "🏁 Done flags in: data/.done/"

# Run tests
test:
	@echo "🧪 Running tests..."
	python -m pytest tests/ -v

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf intermediate/broombridge/*.yaml
	rm -rf data/resource_estimates.csv
	rm -rf data/.done/
	@echo "✅ Cleanup completed"

# Quick sanity check
sanity:
	@echo "🔍 Running sanity check..."
	python scripts/sanity_check.py
