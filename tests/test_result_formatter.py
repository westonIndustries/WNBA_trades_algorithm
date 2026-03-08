"""Unit tests for ResultFormatter"""
import json
import pytest

from src.formatters import ResultFormatter
from src.calculators.brand_portability_calculator import (
    BrandPortabilityResult,
    ComponentBreakdown
)
from src.calculators.revenue_delta_calculator import RevenueDeltaResult
from src.calculators.team_value_lift_calculator import TeamValueLiftResult
from src.calculators.career_baseline_calculator import CareerBaselineResult
from src.calculators.market_adjustment_calculator import MarketAdjustmentResult


@pytest.fixture
def sample_result():
    """Create a sample BrandPortabilityResult for testing"""
    career_baseline = CareerBaselineResult(
        avg_annual_output=5_000_000.0,
        total_years=5,
        annual_breakdown=[
            (2020, 4_500_000.0),
            (2021, 4_800_000.0),
            (2022, 5_200_000.0),
            (2023, 5_300_000.0),
            (2024, 5_200_000.0)
        ]
    )
    
    market_adjustment = MarketAdjustmentResult(
        adjustment_factor=1.2,
        base_tier_factor=1.25,
        dma_adjustment=0.96,
        player_contribution_weight=0.35
    )
    
    revenue_delta = RevenueDeltaResult(
        total_delta=3_000_000.0,
        career_avg_revenue=5_000_000.0,
        new_city_revenue=8_000_000.0,
        components={
            "merchandise": 1_200_000.0,
            "tv_rating": 1_000_000.0,
            "ticket_premium": 800_000.0
        }
    )
    
    team_value_lift = TeamValueLiftResult(
        net_lift=0.07,  # 7% net lift
        team_growth_rate=0.25,
        league_avg_growth_rate=0.18,
        team_valuation_prior=100_000_000.0,
        team_valuation_current=125_000_000.0
    )
    
    components = ComponentBreakdown(
        career_baseline=career_baseline,
        market_adjustment=market_adjustment,
        revenue_delta=revenue_delta,
        team_value_lift=team_value_lift
    )
    
    return BrandPortabilityResult(
        chi=2.45,
        components=components,
        formula="χ = Ch ⋅ Ma / (ΔRm + ΔVt)",
        interpretation="High portability - significant impact expected. This player should have a strong positive effect on team value and revenue.",
        warnings=[]
    )


@pytest.fixture
def result_with_warnings():
    """Create a result with warnings"""
    career_baseline = CareerBaselineResult(
        avg_annual_output=1_000_000.0,
        total_years=2,
        annual_breakdown=[(2023, 1_000_000.0), (2024, 1_000_000.0)]
    )
    
    market_adjustment = MarketAdjustmentResult(
        adjustment_factor=1.0,
        base_tier_factor=1.0,
        dma_adjustment=1.0,
        player_contribution_weight=0.2
    )
    
    revenue_delta = RevenueDeltaResult(
        total_delta=0.0,
        career_avg_revenue=500_000.0,
        new_city_revenue=500_000.0,
        components={"merchandise": 0.0, "tv_rating": 0.0, "ticket_premium": 0.0}
    )
    
    team_value_lift = TeamValueLiftResult(
        net_lift=0.0,
        team_growth_rate=0.15,
        league_avg_growth_rate=0.15,
        team_valuation_prior=50_000_000.0,
        team_valuation_current=57_500_000.0
    )
    
    components = ComponentBreakdown(
        career_baseline=career_baseline,
        market_adjustment=market_adjustment,
        revenue_delta=revenue_delta,
        team_value_lift=team_value_lift
    )
    
    return BrandPortabilityResult(
        chi=100_000.0,  # Very high due to near-zero denominator
        components=components,
        formula="χ = Ch ⋅ Ma / (ΔRm + ΔVt)",
        interpretation="Exceptional portability - star player with massive market impact. This player is expected to significantly boost team value and revenue in the new market.",
        warnings=["Denominator near zero (ΔRm + ΔVt ≈ 0), applied epsilon adjustment (0.01). This indicates the revenue delta and team value lift are offsetting each other."]
    )


class TestResultFormatterToDict:
    """Test to_dict method"""
    
    def test_to_dict_structure(self, sample_result):
        """Test that to_dict produces correct structure"""
        formatter = ResultFormatter()
        result_dict = formatter.to_dict(sample_result)
        
        # Verify top-level keys
        assert set(result_dict.keys()) == {
            "brandPortability", "components", "formula", "interpretation", "warnings"
        }
        
        # Verify brandPortability value
        assert result_dict["brandPortability"] == 2.45
        
        # Verify formula
        assert result_dict["formula"] == "χ = Ch ⋅ Ma / (ΔRm + ΔVt)"
        
        # Verify interpretation
        assert "High portability" in result_dict["interpretation"]
        
        # Verify warnings is empty list
        assert result_dict["warnings"] == []
    
    def test_to_dict_components_structure(self, sample_result):
        """Test that components are correctly structured"""
        formatter = ResultFormatter()
        result_dict = formatter.to_dict(sample_result)
        
        components = result_dict["components"]
        
        # Verify all four components exist
        assert set(components.keys()) == {
            "careerBaseline", "marketAdjustment", "revenueDelta", "teamValueLift"
        }
        
        # Verify careerBaseline
        cb = components["careerBaseline"]
        assert cb["avgAnnualOutput"] == 5_000_000.0
        assert cb["totalYears"] == 5
        assert len(cb["annualBreakdown"]) == 5
        assert cb["annualBreakdown"][0] == [2020, 4_500_000.0]
        
        # Verify marketAdjustment
        ma = components["marketAdjustment"]
        assert ma["adjustmentFactor"] == 1.2
        assert ma["baseTierFactor"] == 1.25
        assert ma["dmaAdjustment"] == 0.96
        assert ma["playerContributionWeight"] == 0.35
        
        # Verify revenueDelta
        rd = components["revenueDelta"]
        assert rd["totalDelta"] == 3_000_000.0
        assert rd["careerAvgRevenue"] == 5_000_000.0
        assert rd["newCityRevenue"] == 8_000_000.0
        assert rd["components"]["merchandise"] == 1_200_000.0
        assert rd["components"]["tv_rating"] == 1_000_000.0
        assert rd["components"]["ticket_premium"] == 800_000.0
        
        # Verify teamValueLift
        tvl = components["teamValueLift"]
        assert tvl["netLift"] == 0.07
        assert tvl["teamGrowthRate"] == 0.25
        assert tvl["leagueAvgGrowthRate"] == 0.18
        assert tvl["teamValuationPrior"] == 100_000_000.0
        assert tvl["teamValuationCurrent"] == 125_000_000.0
    
    def test_to_dict_with_warnings(self, result_with_warnings):
        """Test that warnings are included in output"""
        formatter = ResultFormatter()
        result_dict = formatter.to_dict(result_with_warnings)
        
        assert len(result_dict["warnings"]) == 1
        assert "Denominator near zero" in result_dict["warnings"][0]


class TestResultFormatterToJson:
    """Test to_json method"""
    
    def test_to_json_valid_json(self, sample_result):
        """Test that to_json produces valid JSON"""
        formatter = ResultFormatter()
        json_output = formatter.to_json(sample_result)
        
        # Should be valid JSON
        parsed = json.loads(json_output)
        
        # Should match to_dict output
        expected = formatter.to_dict(sample_result)
        assert parsed == expected
    
    def test_to_json_formatting(self, sample_result):
        """Test that JSON is formatted with indentation"""
        formatter = ResultFormatter()
        json_output = formatter.to_json(sample_result)
        
        # Should have newlines (indented)
        assert "\n" in json_output
        
        # Should have proper indentation
        assert "  " in json_output
    
    def test_to_json_with_warnings(self, result_with_warnings):
        """Test JSON serialization with warnings"""
        formatter = ResultFormatter()
        json_output = formatter.to_json(result_with_warnings)
        
        parsed = json.loads(json_output)
        assert "warnings" in parsed
        assert len(parsed["warnings"]) == 1


class TestResultFormatterToReadableText:
    """Test to_readable_text method"""
    
    def test_to_readable_text_structure(self, sample_result):
        """Test that readable text has expected structure"""
        formatter = ResultFormatter()
        text = formatter.to_readable_text(sample_result)
        
        # Should contain header
        assert "BRAND PORTABILITY ANALYSIS" in text
        
        # Should contain chi value
        assert "Brand Portability Score (χ): 2.45" in text
        
        # Should contain formula
        assert "χ = Ch ⋅ Ma / (ΔRm + ΔVt)" in text
        
        # Should contain interpretation
        assert "INTERPRETATION:" in text
        assert "High portability" in text
        
        # Should contain component breakdown
        assert "COMPONENT BREAKDOWN" in text
        assert "Career Historical Baseline (Ch)" in text
        assert "Market Adjustment Factor (Ma)" in text
        assert "Revenue Delta (ΔRm)" in text
        assert "Team Value Lift (ΔVt)" in text
    
    def test_to_readable_text_values(self, sample_result):
        """Test that readable text contains correct values"""
        formatter = ResultFormatter()
        text = formatter.to_readable_text(sample_result)
        
        # Check career baseline values
        assert "$5,000,000.00" in text
        assert "Total Years: 5" in text
        assert "2020: $4,500,000.00" in text
        
        # Check market adjustment values
        assert "1.200" in text
        assert "1.250" in text
        
        # Check revenue delta values
        assert "$3,000,000.00" in text
        assert "$8,000,000.00" in text
        
        # Check team value lift values
        assert "7.00%" in text
        assert "25.00%" in text
        assert "18.00%" in text
    
    def test_to_readable_text_with_warnings(self, result_with_warnings):
        """Test that warnings are displayed in readable text"""
        formatter = ResultFormatter()
        text = formatter.to_readable_text(result_with_warnings)
        
        assert "WARNINGS:" in text
        assert "⚠" in text
        assert "Denominator near zero" in text


class TestGenerateInterpretation:
    """Test generate_interpretation method"""
    
    def test_interpretation_exceptional(self):
        """Test interpretation for chi > 3.0"""
        formatter = ResultFormatter()
        interpretation = formatter.generate_interpretation(3.5)
        
        assert "Exceptional portability" in interpretation
        assert "massive market impact" in interpretation
    
    def test_interpretation_high(self):
        """Test interpretation for 2.0 < chi ≤ 3.0"""
        formatter = ResultFormatter()
        interpretation = formatter.generate_interpretation(2.5)
        
        assert "High portability" in interpretation
        assert "significant impact" in interpretation
    
    def test_interpretation_moderate(self):
        """Test interpretation for 1.0 < chi ≤ 2.0"""
        formatter = ResultFormatter()
        interpretation = formatter.generate_interpretation(1.5)
        
        assert "Moderate portability" in interpretation
        assert "average impact" in interpretation
    
    def test_interpretation_low(self):
        """Test interpretation for 0.5 < chi ≤ 1.0"""
        formatter = ResultFormatter()
        interpretation = formatter.generate_interpretation(0.75)
        
        assert "Low portability" in interpretation
        assert "limited impact" in interpretation
    
    def test_interpretation_minimal(self):
        """Test interpretation for chi ≤ 0.5"""
        formatter = ResultFormatter()
        interpretation = formatter.generate_interpretation(0.3)
        
        assert "Minimal portability" in interpretation
        assert "negligible impact" in interpretation
    
    def test_interpretation_boundary_values(self):
        """Test interpretation at boundary values"""
        formatter = ResultFormatter()
        
        # Test exactly 3.0 (should be high, not exceptional)
        assert "High portability" in formatter.generate_interpretation(3.0)
        
        # Test exactly 2.0 (should be moderate, not high)
        assert "Moderate portability" in formatter.generate_interpretation(2.0)
        
        # Test exactly 1.0 (should be low, not moderate)
        assert "Low portability" in formatter.generate_interpretation(1.0)
        
        # Test exactly 0.5 (should be minimal, not low)
        assert "Minimal portability" in formatter.generate_interpretation(0.5)
    
    def test_interpretation_edge_cases(self):
        """Test interpretation for edge cases"""
        formatter = ResultFormatter()
        
        # Test zero
        assert "Minimal portability" in formatter.generate_interpretation(0.0)
        
        # Test very high value
        assert "Exceptional portability" in formatter.generate_interpretation(10.0)
        
        # Test just above 3.0
        assert "Exceptional portability" in formatter.generate_interpretation(3.01)
