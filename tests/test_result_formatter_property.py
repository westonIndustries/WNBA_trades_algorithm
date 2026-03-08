"""Property-based tests for ResultFormatter"""
import pytest
from hypothesis import given, strategies as st

from src.formatters import ResultFormatter
from src.calculators.brand_portability_calculator import (
    BrandPortabilityResult,
    ComponentBreakdown
)
from src.calculators.revenue_delta_calculator import RevenueDeltaResult
from src.calculators.team_value_lift_calculator import TeamValueLiftResult
from src.calculators.career_baseline_calculator import CareerBaselineResult
from src.calculators.market_adjustment_calculator import MarketAdjustmentResult


# Strategy for generating valid annual breakdown data
@st.composite
def annual_breakdown_strategy(draw):
    """Generate valid annual breakdown list"""
    num_years = draw(st.integers(min_value=1, max_value=10))
    start_year = draw(st.integers(min_value=2015, max_value=2024))
    
    breakdown = []
    for i in range(num_years):
        year = start_year + i
        output = draw(st.floats(min_value=0.0, max_value=1e7, allow_nan=False, allow_infinity=False))
        breakdown.append((year, output))
    
    return breakdown


# Strategy for generating valid component results
@st.composite
def component_breakdown_strategy(draw):
    """Generate valid ComponentBreakdown"""
    # Career Baseline
    annual_breakdown = draw(annual_breakdown_strategy())
    avg_output = sum(output for _, output in annual_breakdown) / len(annual_breakdown)
    career_baseline = CareerBaselineResult(
        avg_annual_output=avg_output,
        total_years=len(annual_breakdown),
        annual_breakdown=annual_breakdown
    )
    
    # Market Adjustment
    base_tier = draw(st.sampled_from([0.85, 1.0, 1.25]))
    dma_adj = draw(st.floats(min_value=0.5, max_value=1.5, allow_nan=False, allow_infinity=False))
    contrib_weight = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
    market_adjustment = MarketAdjustmentResult(
        adjustment_factor=base_tier * dma_adj * (1.0 + contrib_weight * 0.5),
        base_tier_factor=base_tier,
        dma_adjustment=dma_adj,
        player_contribution_weight=contrib_weight
    )
    
    # Revenue Delta
    career_avg = draw(st.floats(min_value=0.0, max_value=1e7, allow_nan=False, allow_infinity=False))
    new_city = draw(st.floats(min_value=0.0, max_value=1e7, allow_nan=False, allow_infinity=False))
    merch_delta = draw(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
    tv_delta = draw(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
    ticket_delta = draw(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
    
    revenue_delta = RevenueDeltaResult(
        total_delta=new_city - career_avg,
        career_avg_revenue=career_avg,
        new_city_revenue=new_city,
        components={
            "merchandise": merch_delta,
            "tv_rating": tv_delta,
            "ticket_premium": ticket_delta
        }
    )
    
    # Team Value Lift
    prior_val = draw(st.floats(min_value=1e6, max_value=1e9, allow_nan=False, allow_infinity=False))
    current_val = draw(st.floats(min_value=1e6, max_value=1e9, allow_nan=False, allow_infinity=False))
    team_growth = (current_val - prior_val) / prior_val
    league_growth = draw(st.floats(min_value=-0.5, max_value=0.5, allow_nan=False, allow_infinity=False))
    
    team_value_lift = TeamValueLiftResult(
        net_lift=team_growth - league_growth,
        team_growth_rate=team_growth,
        league_avg_growth_rate=league_growth,
        team_valuation_prior=prior_val,
        team_valuation_current=current_val
    )
    
    return ComponentBreakdown(
        career_baseline=career_baseline,
        market_adjustment=market_adjustment,
        revenue_delta=revenue_delta,
        team_value_lift=team_value_lift
    )


# Strategy for generating valid BrandPortabilityResult
@st.composite
def brand_portability_result_strategy(draw):
    """Generate valid BrandPortabilityResult"""
    chi = draw(st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False))
    components = draw(component_breakdown_strategy())
    formula = "χ = Ch ⋅ Ma / (ΔRm + ΔVt)"
    
    # Generate interpretation based on chi
    if chi > 3.0:
        interpretation = "Exceptional portability"
    elif chi > 2.0:
        interpretation = "High portability"
    elif chi > 1.0:
        interpretation = "Moderate portability"
    elif chi > 0.5:
        interpretation = "Low portability"
    else:
        interpretation = "Minimal portability"
    
    # Generate warnings
    num_warnings = draw(st.integers(min_value=0, max_value=3))
    warnings = [f"Warning {i}" for i in range(num_warnings)]
    
    return BrandPortabilityResult(
        chi=chi,
        components=components,
        formula=formula,
        interpretation=interpretation,
        warnings=warnings
    )


# Feature: brand-portability-formula, Property 15: Output structure completeness
@given(result=brand_portability_result_strategy())
def test_output_structure_completeness(result):
    """
    Property 15: Output structure completeness
    
    For any successful brand portability calculation, the output should contain
    all required fields: brandPortability (chi value), components (with all four
    sub-components), formula string, interpretation string, and warnings array.
    
    Validates: Requirements - Output Requirements, Acceptance Criteria 5
    """
    formatter = ResultFormatter()
    
    # Test to_dict output
    output_dict = formatter.to_dict(result)
    
    # Verify top-level fields exist
    assert "brandPortability" in output_dict
    assert "components" in output_dict
    assert "formula" in output_dict
    assert "interpretation" in output_dict
    assert "warnings" in output_dict
    
    # Verify brandPortability is a number
    assert isinstance(output_dict["brandPortability"], (int, float))
    
    # Verify components has all four sub-components
    components = output_dict["components"]
    assert "careerBaseline" in components
    assert "marketAdjustment" in components
    assert "revenueDelta" in components
    assert "teamValueLift" in components
    
    # Verify careerBaseline structure
    career_baseline = components["careerBaseline"]
    assert "avgAnnualOutput" in career_baseline
    assert "totalYears" in career_baseline
    assert "annualBreakdown" in career_baseline
    assert isinstance(career_baseline["avgAnnualOutput"], (int, float))
    assert isinstance(career_baseline["totalYears"], int)
    assert isinstance(career_baseline["annualBreakdown"], list)
    
    # Verify marketAdjustment structure
    market_adjustment = components["marketAdjustment"]
    assert "adjustmentFactor" in market_adjustment
    assert "baseTierFactor" in market_adjustment
    assert "dmaAdjustment" in market_adjustment
    assert "playerContributionWeight" in market_adjustment
    assert isinstance(market_adjustment["adjustmentFactor"], (int, float))
    assert isinstance(market_adjustment["baseTierFactor"], (int, float))
    assert isinstance(market_adjustment["dmaAdjustment"], (int, float))
    assert isinstance(market_adjustment["playerContributionWeight"], (int, float))
    
    # Verify revenueDelta structure
    revenue_delta = components["revenueDelta"]
    assert "totalDelta" in revenue_delta
    assert "careerAvgRevenue" in revenue_delta
    assert "newCityRevenue" in revenue_delta
    assert "components" in revenue_delta
    assert isinstance(revenue_delta["totalDelta"], (int, float))
    assert isinstance(revenue_delta["careerAvgRevenue"], (int, float))
    assert isinstance(revenue_delta["newCityRevenue"], (int, float))
    assert isinstance(revenue_delta["components"], dict)
    
    # Verify revenueDelta components
    rd_components = revenue_delta["components"]
    assert "merchandise" in rd_components
    assert "tv_rating" in rd_components
    assert "ticket_premium" in rd_components
    
    # Verify teamValueLift structure
    team_value_lift = components["teamValueLift"]
    assert "netLift" in team_value_lift
    assert "teamGrowthRate" in team_value_lift
    assert "leagueAvgGrowthRate" in team_value_lift
    assert "teamValuationPrior" in team_value_lift
    assert "teamValuationCurrent" in team_value_lift
    assert isinstance(team_value_lift["netLift"], (int, float))
    assert isinstance(team_value_lift["teamGrowthRate"], (int, float))
    assert isinstance(team_value_lift["leagueAvgGrowthRate"], (int, float))
    assert isinstance(team_value_lift["teamValuationPrior"], (int, float))
    assert isinstance(team_value_lift["teamValuationCurrent"], (int, float))
    
    # Verify formula is a string
    assert isinstance(output_dict["formula"], str)
    assert len(output_dict["formula"]) > 0
    
    # Verify interpretation is a string
    assert isinstance(output_dict["interpretation"], str)
    assert len(output_dict["interpretation"]) > 0
    
    # Verify warnings is a list
    assert isinstance(output_dict["warnings"], list)
    
    # Test to_json output
    json_output = formatter.to_json(result)
    assert isinstance(json_output, str)
    assert len(json_output) > 0
    
    # Verify JSON is valid by parsing it
    import json
    parsed = json.loads(json_output)
    assert parsed == output_dict
    
    # Test to_readable_text output
    text_output = formatter.to_readable_text(result)
    assert isinstance(text_output, str)
    assert len(text_output) > 0
    assert "BRAND PORTABILITY ANALYSIS" in text_output
    assert "Brand Portability Score" in text_output
    assert "COMPONENT BREAKDOWN" in text_output
