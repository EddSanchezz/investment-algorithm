"""
Tests unitarios para PDFReportGenerator (src.services.reporting.pdf_report).
"""

import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.services.reporting.pdf_report import PDFReportGenerator


class TestPDFReportGenerator:
    def setup_method(self):
        self.generator = PDFReportGenerator()
        self.tmpdir = tempfile.mkdtemp()

    def test_initialization(self):
        assert self.generator is not None
        assert hasattr(self.generator, "styles")

    def test_add_cover_page(self):
        self.generator.add_cover_page()
        assert len(self.generator.elements) > 0

    def test_add_portfolio_summary(self):
        records = [
            {"symbol": "VOO", "close": 100.0, "volume": 1000, "date": "2024-01-01"},
            {"symbol": "IVV", "close": 200.0, "volume": 2000, "date": "2024-01-01"},
        ]
        self.generator.add_portfolio_summary(records)
        assert len(self.generator.elements) > 0

    def test_add_risk_ranking(self):
        rankings = {"ranking": [
            {"symbol": "VOO", "risk_category": "conservador", "annualized_volatility_pct": 15.0,
             "daily_std": 0.01, "mean_daily_return_pct": 0.05},
            {"symbol": "IVV", "risk_category": "moderado", "annualized_volatility_pct": 25.0,
             "daily_std": 0.02, "mean_daily_return_pct": 0.08},
        ]}
        self.generator.add_risk_ranking(rankings)
        assert len(self.generator.elements) > 0

    def test_save_generates_pdf(self):
        self.generator.add_cover_page()
        output_path = os.path.join(self.tmpdir, "test.pdf")
        self.generator.save(output_path)
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_save_with_similarity_table(self):
        sim_data = {
            "euclidean": {"distance": 0.5},
            "pearson": {"correlation": 0.9},
            "dtw": {"distance": 10.0},
            "cosine": {"similarity": 0.95},
            "symbols": {"a": "VOO", "b": "IVV"},
        }
        self.generator.add_similarity_table(sim_data)
        self.generator.add_cover_page()
        output_path = os.path.join(self.tmpdir, "test_table.pdf")
        self.generator.save(output_path)
        assert os.path.exists(output_path)
