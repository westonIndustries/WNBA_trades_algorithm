"""Unit tests for JSONLoader"""
import pytest
import json
import tempfile
from pathlib import Path

from src.data_loaders import JSONLoader
from src.models import MarketTierData


class TestJSONLoader:
    """Test JSONLoader class"""
    
    def test_load_market_tiers_2024_valid_file(self):
        """Test loading valid 2024 market tiers JSON"""
        loader = JSONLoader()
        result = loader.load_market_tiers_2024("data/WNBA 2024 market tiers data.json")
        
        # Verify structure
        assert "tiers" in result
        assert "team_records_2024" in result
        assert "team_records_2023" in result
        
        # Verify tiers
        assert len(result["tiers"]) == 3
        
        # Check Tier 1
        tier1_found = False
        for tier_name, tier_data in result["tiers"].items():
            if "Tier 1" in tier_name:
                tier1_found = True
                assert isinstance(tier_data, MarketTierData)
                assert tier_data.tier == 1
                assert tier_data.adjustment_factor == 1.25
                assert len(tier_data.teams) == 3
                assert "Las Vegas Aces" in tier_data.teams
        
        assert tier1_found, "Tier 1 not found in results"
        
        # Verify team records
        assert len(result["team_records_2024"]) > 0
        assert len(result["team_records_2023"]) > 0
        
        # Check a specific team record
        for team_name, record in result["team_records_2024"]:
            if team_name == "Las Vegas Aces":
                assert record.year == 2024
                assert record.valuation == 140_000_000  # 140M
                break
    
    def test_load_market_tiers_2026_valid_file(self):
        """Test loading valid 2026 market tiers JSON"""
        loader = JSONLoader()
        result = loader.load_market_tiers_2026("data/WNBA 2026 Market Tiers.json")
        
        # Verify structure
        assert "tiers" in result
        assert "team_dma_rankings" in result
        assert "team_valuations_2026" in result
        
        # Verify tiers
        assert len(result["tiers"]) == 3
        
        # Check Tier 1
        tier1 = result["tiers"]["Tier 1"]
        assert isinstance(tier1, MarketTierData)
        assert tier1.tier == 1
        assert tier1.adjustment_factor == 1.25
        assert "Golden State Valkyries" in tier1.teams
        
        # Verify DMA rankings
        assert "New York Liberty" in result["team_dma_rankings"]
        assert result["team_dma_rankings"]["New York Liberty"] == 1
        
        # Verify valuations
        assert len(result["team_valuations_2026"]) > 0
        for team_name, record in result["team_valuations_2026"]:
            if team_name == "Golden State Valkyries":
                assert record.year == 2026
                assert record.valuation == 500_000_000  # 500M
                break
    
    def test_load_market_tiers_2024_file_not_found(self):
        """Test error handling for missing file"""
        loader = JSONLoader()
        
        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load_market_tiers_2024("nonexistent.json")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_load_market_tiers_2024_malformed_json(self):
        """Test error handling for malformed JSON"""
        loader = JSONLoader()
        
        # Create temporary malformed JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                loader.load_market_tiers_2024(temp_path)
            
            assert "malformed" in str(exc_info.value).lower()
        finally:
            Path(temp_path).unlink()
    
    def test_load_market_tiers_2024_missing_key(self):
        """Test error handling for missing required key"""
        loader = JSONLoader()
        
        # Create temporary JSON with missing key
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"wrong_key": {}}, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                loader.load_market_tiers_2024(temp_path)
            
            assert "WNBA_Market_Data_2024" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()
    
    def test_load_market_tiers_2026_file_not_found(self):
        """Test error handling for missing 2026 file"""
        loader = JSONLoader()
        
        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load_market_tiers_2026("nonexistent.json")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_load_market_tiers_2026_missing_key(self):
        """Test error handling for missing required key in 2026 data"""
        loader = JSONLoader()
        
        # Create temporary JSON with missing key
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"wrong_key": {}}, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                loader.load_market_tiers_2026(temp_path)
            
            assert "WNBA_Market_Data" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()
