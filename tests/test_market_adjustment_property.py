"""Property-based tests for Market Adjustment Calculator"""
import pytest
from hypothesis import given, strategies as st, assume

from src.calculators import MarketAdjustmentCalculator
from src.models import TeamData, TeamAnnualRecord, MarketTierData


# Feature: brand-portability-formula, Property 5: Market adjustment calculation
# Validates: Requirements - Ma Definition
@given(
    market_tier=st.integers(min_value=1, max_value=3),
    dma_ranking=st.integers(min_value=1, max_value=210),
    player_contribution_weight=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
def test_market_adjustment_incorporates_all_factors(market_tier, dma_ranking, player_contribution_weight):
    """
    Property 5: Market adjustment calculation
    
    For any team with market tier classification, DMA ranking, and player contribution
    weight, the market adjustment (Ma) should incorporate all three factors in the final value.
    
    The adjustment factor should:
    1. Be influenced by the base tier factor (1.25, 1.0, or 0.85)
    2. Be influenced by DMA ranking (lower ranking = larger market = higher adjustment)
    3. Be influenced by player contribution weight (higher weight = higher adjustment)
    
    **Validates: Requirements - Ma Definition**
    """
    # Map market tier to expected base factor
    tier_to_factor = {1: 1.25, 2: 1.0, 3: 0.85}
    expected_base_factor = tier_to_factor[market_tier]
    
    # Create market tier data
    market_tier_data = MarketTierData(
        tier=market_tier,
        adjustment_factor=expected_base_factor,
        teams=["TEAM1"]
    )
    
    # Create team data
    team_data = TeamData(
        team_id="TEAM1",
        team_name="Test Team",
        market_tier=market_tier,
        dma_ranking=dma_ranking,
        annual_records=[
            TeamAnnualRecord(
                year=2024,
                valuation=100_000_000,
                revenue=10_000_000,
                attendance_avg=10000,
                points_per_game=80.0
            )
        ]
    )
    
    # Create calculator
    calculator = MarketAdjustmentCalculator()
    
    # Calculate market adjustment
    result = calculator.calculate(team_data, market_tier_data, player_contribution_weight)
    
    # Property 1: Base tier factor should match the market tier
    assert result.base_tier_factor == expected_base_factor, (
        f"Base tier factor {result.base_tier_factor} should equal {expected_base_factor}"
    )
    
    # Property 2: DMA adjustment should be within valid bounds (0.5 to 1.5)
    assert 0.5 <= result.dma_adjustment <= 1.5, (
        f"DMA adjustment {result.dma_adjustment} should be between 0.5 and 1.5"
    )
    
    # Property 3: Player contribution weight should be stored correctly
    assert abs(result.player_contribution_weight - player_contribution_weight) < 0.001, (
        f"Player contribution weight {result.player_contribution_weight} should equal {player_contribution_weight}"
    )
    
    # Property 4: Lower DMA ranking should result in higher DMA adjustment
    # Test by comparing with a higher DMA ranking
    if dma_ranking < 210:
        team_data_higher_dma = TeamData(
            team_id="TEAM2",
            team_name="Test Team 2",
            market_tier=market_tier,
            dma_ranking=min(dma_ranking + 50, 210),
            annual_records=team_data.annual_records
        )
        
        result_higher_dma = calculator.calculate(
            team_data_higher_dma,
            market_tier_data,
            player_contribution_weight
        )
        
        # Lower DMA ranking should have higher or equal adjustment
        assert result.dma_adjustment >= result_higher_dma.dma_adjustment, (
            f"Lower DMA ranking {dma_ranking} should have higher adjustment "
            f"({result.dma_adjustment}) than higher ranking "
            f"{dma_ranking + 50} ({result_higher_dma.dma_adjustment})"
        )
    
    # Property 5: Higher player contribution weight should result in higher adjustment factor
    if player_contribution_weight < 1.0:
        higher_weight = min(player_contribution_weight + 0.1, 1.0)
        result_higher_weight = calculator.calculate(
            team_data,
            market_tier_data,
            higher_weight
        )
        
        assert result_higher_weight.adjustment_factor >= result.adjustment_factor, (
            f"Higher player contribution weight {higher_weight} should result in "
            f"higher adjustment factor ({result_higher_weight.adjustment_factor}) "
            f"than lower weight {player_contribution_weight} ({result.adjustment_factor})"
        )
    
    # Property 6: Adjustment factor should be positive
    assert result.adjustment_factor > 0, (
        f"Adjustment factor should be positive, got {result.adjustment_factor}"
    )
    
    # Property 7: Adjustment factor should incorporate all three components
    # Formula: Ma = base_tier_factor × dma_adjustment × (1 + player_contribution_weight × 0.5)
    expected_adjustment = (
        result.base_tier_factor *
        result.dma_adjustment *
        (1.0 + player_contribution_weight * 0.5)
    )
    
    assert abs(result.adjustment_factor - expected_adjustment) < 0.001, (
        f"Adjustment factor {result.adjustment_factor} should equal "
        f"calculated value {expected_adjustment}"
    )


# Feature: brand-portability-formula, Property 5: Market adjustment calculation (tier comparison)
# Validates: Requirements - Ma Definition
@given(
    dma_ranking=st.integers(min_value=1, max_value=210),
    player_contribution_weight=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
def test_market_adjustment_tier_ordering(dma_ranking, player_contribution_weight):
    """
    Property 5: Market adjustment calculation (tier comparison)
    
    For the same DMA ranking and player contribution weight, Tier 1 markets should
    have higher base adjustment factors than Tier 2, which should be higher than Tier 3.
    
    Tier 1: 1.25
    Tier 2: 1.0
    Tier 3: 0.85
    
    **Validates: Requirements - Ma Definition**
    """
    calculator = MarketAdjustmentCalculator()
    
    # Create team data for each tier
    results = {}
    for tier in [1, 2, 3]:
        tier_to_factor = {1: 1.25, 2: 1.0, 3: 0.85}
        
        market_tier_data = MarketTierData(
            tier=tier,
            adjustment_factor=tier_to_factor[tier],
            teams=[f"TEAM{tier}"]
        )
        
        team_data = TeamData(
            team_id=f"TEAM{tier}",
            team_name=f"Test Team {tier}",
            market_tier=tier,
            dma_ranking=dma_ranking,
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=100_000_000,
                    revenue=10_000_000,
                    attendance_avg=10000,
                    points_per_game=80.0
                )
            ]
        )
        
        results[tier] = calculator.calculate(team_data, market_tier_data, player_contribution_weight)
    
    # Property: Tier 1 should have higher base factor than Tier 2
    assert results[1].base_tier_factor > results[2].base_tier_factor, (
        f"Tier 1 base factor {results[1].base_tier_factor} should be greater than "
        f"Tier 2 base factor {results[2].base_tier_factor}"
    )
    
    # Property: Tier 2 should have higher base factor than Tier 3
    assert results[2].base_tier_factor > results[3].base_tier_factor, (
        f"Tier 2 base factor {results[2].base_tier_factor} should be greater than "
        f"Tier 3 base factor {results[3].base_tier_factor}"
    )
    
    # Property: Since DMA and player weight are the same, adjustment factors should follow same ordering
    assert results[1].adjustment_factor > results[2].adjustment_factor, (
        f"Tier 1 adjustment {results[1].adjustment_factor} should be greater than "
        f"Tier 2 adjustment {results[2].adjustment_factor}"
    )
    
    assert results[2].adjustment_factor > results[3].adjustment_factor, (
        f"Tier 2 adjustment {results[2].adjustment_factor} should be greater than "
        f"Tier 3 adjustment {results[3].adjustment_factor}"
    )


# Feature: brand-portability-formula, Property 5: Market adjustment calculation (DMA impact)
# Validates: Requirements - Ma Definition
@given(
    market_tier=st.integers(min_value=1, max_value=3),
    player_contribution_weight=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
def test_market_adjustment_dma_impact(market_tier, player_contribution_weight):
    """
    Property 5: Market adjustment calculation (DMA impact)
    
    For the same market tier and player contribution weight, lower DMA rankings
    (larger markets) should result in higher adjustment factors.
    
    **Validates: Requirements - Ma Definition**
    """
    tier_to_factor = {1: 1.25, 2: 1.0, 3: 0.85}
    
    market_tier_data = MarketTierData(
        tier=market_tier,
        adjustment_factor=tier_to_factor[market_tier],
        teams=["TEAM1", "TEAM2", "TEAM3"]
    )
    
    calculator = MarketAdjustmentCalculator()
    
    # Test with three different DMA rankings: small, medium, large markets
    dma_rankings = [1, 50, 200]  # New York, mid-size, small market
    results = []
    
    for dma in dma_rankings:
        team_data = TeamData(
            team_id=f"TEAM_DMA{dma}",
            team_name=f"Test Team DMA {dma}",
            market_tier=market_tier,
            dma_ranking=dma,
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=100_000_000,
                    revenue=10_000_000,
                    attendance_avg=10000,
                    points_per_game=80.0
                )
            ]
        )
        
        result = calculator.calculate(team_data, market_tier_data, player_contribution_weight)
        results.append((dma, result))
    
    # Property: Lower DMA ranking should have higher adjustment factor
    # DMA 1 > DMA 50 > DMA 200
    assert results[0][1].adjustment_factor >= results[1][1].adjustment_factor, (
        f"DMA 1 adjustment {results[0][1].adjustment_factor} should be >= "
        f"DMA 50 adjustment {results[1][1].adjustment_factor}"
    )
    
    assert results[1][1].adjustment_factor >= results[2][1].adjustment_factor, (
        f"DMA 50 adjustment {results[1][1].adjustment_factor} should be >= "
        f"DMA 200 adjustment {results[2][1].adjustment_factor}"
    )
    
    # Property: DMA adjustments should be within bounds
    for dma, result in results:
        assert 0.5 <= result.dma_adjustment <= 1.5, (
            f"DMA {dma} adjustment {result.dma_adjustment} should be between 0.5 and 1.5"
        )



# Feature: brand-portability-formula, Property 12: Market adjustment factor bounds
# Validates: Requirements - Ma Definition
@given(
    market_tier=st.integers(min_value=1, max_value=3),
    dma_ranking=st.integers(min_value=1, max_value=210),
    player_contribution_weight=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
def test_market_adjustment_base_factor_bounds(market_tier, dma_ranking, player_contribution_weight):
    """
    Property 12: Market adjustment factor bounds
    
    For any valid market tier (1, 2, or 3), the base market adjustment factor should
    be one of the three valid values: 1.25 (Tier 1), 1.0 (Tier 2), or 0.85 (Tier 3).
    
    **Validates: Requirements - Ma Definition**
    """
    # Map market tier to expected base factor
    tier_to_factor = {1: 1.25, 2: 1.0, 3: 0.85}
    expected_base_factor = tier_to_factor[market_tier]
    
    # Create market tier data
    market_tier_data = MarketTierData(
        tier=market_tier,
        adjustment_factor=expected_base_factor,
        teams=["TEAM1"]
    )
    
    # Create team data
    team_data = TeamData(
        team_id="TEAM1",
        team_name="Test Team",
        market_tier=market_tier,
        dma_ranking=dma_ranking,
        annual_records=[
            TeamAnnualRecord(
                year=2024,
                valuation=100_000_000,
                revenue=10_000_000,
                attendance_avg=10000,
                points_per_game=80.0
            )
        ]
    )
    
    # Create calculator
    calculator = MarketAdjustmentCalculator()
    
    # Calculate market adjustment
    result = calculator.calculate(team_data, market_tier_data, player_contribution_weight)
    
    # Property: Base tier factor must be one of the three valid values
    valid_factors = [1.25, 1.0, 0.85]
    assert result.base_tier_factor in valid_factors, (
        f"Base tier factor {result.base_tier_factor} must be one of {valid_factors}"
    )
    
    # Property: Base tier factor must match the expected value for the tier
    assert abs(result.base_tier_factor - expected_base_factor) < 0.001, (
        f"Base tier factor {result.base_tier_factor} should equal {expected_base_factor} "
        f"for market tier {market_tier}"
    )
    
    # Property: Tier 1 should always have factor 1.25
    if market_tier == 1:
        assert abs(result.base_tier_factor - 1.25) < 0.001, (
            f"Tier 1 should have base factor 1.25, got {result.base_tier_factor}"
        )
    
    # Property: Tier 2 should always have factor 1.0
    if market_tier == 2:
        assert abs(result.base_tier_factor - 1.0) < 0.001, (
            f"Tier 2 should have base factor 1.0, got {result.base_tier_factor}"
        )
    
    # Property: Tier 3 should always have factor 0.85
    if market_tier == 3:
        assert abs(result.base_tier_factor - 0.85) < 0.001, (
            f"Tier 3 should have base factor 0.85, got {result.base_tier_factor}"
        )


# Feature: brand-portability-formula, Property 12: Market adjustment factor bounds (validation)
# Validates: Requirements - Ma Definition
def test_market_adjustment_invalid_tier_raises_error():
    """
    Property 12: Market adjustment factor bounds (validation)
    
    When an invalid market tier is provided (not 1, 2, or 3), the calculator
    should raise a ValueError.
    
    **Validates: Requirements - Ma Definition**
    """
    calculator = MarketAdjustmentCalculator()
    
    # Test with invalid market tiers
    invalid_tiers = [0, 4, -1, 10]
    
    for invalid_tier in invalid_tiers:
        market_tier_data = MarketTierData(
            tier=invalid_tier,
            adjustment_factor=1.0,
            teams=["TEAM1"]
        )
        
        team_data = TeamData(
            team_id="TEAM1",
            team_name="Test Team",
            market_tier=invalid_tier,
            dma_ranking=25,
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=100_000_000,
                    revenue=10_000_000,
                    attendance_avg=10000,
                    points_per_game=80.0
                )
            ]
        )
        
        # Should raise ValueError for invalid market tier
        with pytest.raises(ValueError, match="Invalid market tier"):
            calculator.calculate(team_data, market_tier_data, 0.5)


# Feature: brand-portability-formula, Property 12: Market adjustment factor bounds (player weight validation)
# Validates: Requirements - Ma Definition
def test_market_adjustment_invalid_player_weight_raises_error():
    """
    Property 12: Market adjustment factor bounds (player weight validation)
    
    When an invalid player contribution weight is provided (not between 0.0 and 1.0),
    the calculator should raise a ValueError.
    
    **Validates: Requirements - Ma Definition**
    """
    calculator = MarketAdjustmentCalculator()
    
    market_tier_data = MarketTierData(
        tier=2,
        adjustment_factor=1.0,
        teams=["TEAM1"]
    )
    
    team_data = TeamData(
        team_id="TEAM1",
        team_name="Test Team",
        market_tier=2,
        dma_ranking=25,
        annual_records=[
            TeamAnnualRecord(
                year=2024,
                valuation=100_000_000,
                revenue=10_000_000,
                attendance_avg=10000,
                points_per_game=80.0
            )
        ]
    )
    
    # Test with invalid player contribution weights
    invalid_weights = [-0.1, 1.1, -1.0, 2.0, 100.0]
    
    for invalid_weight in invalid_weights:
        # Should raise ValueError for invalid player contribution weight
        with pytest.raises(ValueError, match="Player contribution weight must be between"):
            calculator.calculate(team_data, market_tier_data, invalid_weight)
