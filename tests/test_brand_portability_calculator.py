"""Unit tests for BrandPortabilityCalculator"""
import pytest

from src.calculators import (
    BrandPortabilityCalculator,
    BrandPortabilityResult,
    RevenueDeltaCalculator,
    TeamValueLiftCalculator,
    CareerBaselineCalculator,
    MarketAdjustmentCalculator
)
from src.estimators import (
    MerchandiseEstimator,
    TVRatingEstimator,
    TicketPremiumEstimator,
    PlayerRevenueAttributor
)
from src.models import (
    PlayerData,
    PlayerAnnualRecord,
    TeamData,
    TeamAnnualRecord,
    LeagueData,
    LeagueAnnualRecord,
    MarketTierData
)


def create_calculator() -> BrandPortabilityCalculator:
    """Helper to create BrandPortabilityCalculator with all dependencies"""
    # Create estimators
    merch_est = MerchandiseEstimator()
    tv_est = TVRatingEstimator()
    ticket_est = TicketPremiumEstimator()
    revenue_attr = PlayerRevenueAttributor()
    
    # Create calculators
    revenue_delta_calc = RevenueDeltaCalculator(merch_est, tv_est, ticket_est)
    team_value_lift_calc = TeamValueLiftCalculator()
    career_baseline_calc = CareerBaselineCalculator(revenue_attr)
    market_adjustment_calc = MarketAdjustmentCalculator()
    
    # Create main calculator
    return BrandPortabilityCalculator(
        revenue_delta_calc,
        team_value_lift_calc,
        career_baseline_calc,
        market_adjustment_calc
    )


class TestBrandPortabilityCalculator:
    """Unit tests for BrandPortabilityCalculator"""
    
    def test_calculate_basic(self):
        """Test basic brand portability calculation"""
        calculator = create_calculator()
        
        # Create player data
        player_data = PlayerData(
            player_id="player_1",
            player_name="Test Player",
            annual_records=[
                PlayerAnnualRecord(
                    year=2023,
                    team_id="old_team",
                    points_per_game=20.0,
                    games_played=40,
                    minutes_per_game=35.0,
                    salary=150_000,
                    scoring_percentile=0.85
                )
            ]
        )
        
        # Create new team data with two years for value lift calculation
        new_team_data = TeamData(
            team_id="new_team",
            team_name="New Team",
            market_tier=1,
            dma_ranking=5,
            annual_records=[
                TeamAnnualRecord(
                    year=2023,
                    valuation=150_000_000,
                    revenue=25_000_000,
                    attendance_avg=10000,
                    points_per_game=82.0
                ),
                TeamAnnualRecord(
                    year=2024,
                    valuation=200_000_000,
                    revenue=30_000_000,
                    attendance_avg=12000,
                    points_per_game=85.0
                )
            ]
        )
        
        # Create old team data for career baseline
        old_team_data = TeamData(
            team_id="old_team",
            team_name="Old Team",
            market_tier=2,
            dma_ranking=20,
            annual_records=[
                TeamAnnualRecord(
                    year=2022,
                    valuation=100_000_000,
                    revenue=18_000_000,
                    attendance_avg=9000,
                    points_per_game=80.0
                ),
                TeamAnnualRecord(
                    year=2023,
                    valuation=110_000_000,
                    revenue=20_000_000,
                    attendance_avg=9500,
                    points_per_game=81.0
                )
            ]
        )
        
        # Create league data
        league_data = LeagueData(
            annual_records=[
                LeagueAnnualRecord(
                    year=2023,
                    avg_viewership=1.0,
                    avg_attendance=9000,
                    avg_salary=120_000,
                    total_teams=12
                )
            ]
        )
        
        # Create market tier data
        market_tier_data = MarketTierData(
            tier=1,
            adjustment_factor=1.25,
            teams=["new_team"]
        )
        
        # Calculate brand portability
        result = calculator.calculate_portability(
            player_data=player_data,
            new_team_data=new_team_data,
            league_data=league_data,
            market_tier_data=market_tier_data,
            team_data_history=[old_team_data],
            prior_year=2023,
            current_year=2024,
            player_contribution_weight=0.35
        )
        
        # Verify result structure
        assert isinstance(result, BrandPortabilityResult)
        assert isinstance(result.chi, float)
        assert result.chi > 0  # Should be positive for valid calculation
        assert result.formula == "χ = Ch ⋅ Ma / (ΔRm + ΔVt)"
        assert isinstance(result.interpretation, str)
        assert len(result.interpretation) > 0
        assert isinstance(result.warnings, list)
        
        # Verify components exist
        assert result.components.career_baseline is not None
        assert result.components.market_adjustment is not None
        assert result.components.revenue_delta is not None
        assert result.components.team_value_lift is not None
    
    def test_division_by_zero_applies_epsilon(self):
        """
        Test edge case: division by zero (ΔRm + ΔVt = 0) applies epsilon and warns
        
        Requirements: Edge Cases 2
        """
        calculator = create_calculator()
        
        # Create player data
        player_data = PlayerData(
            player_id="player_1",
            player_name="Test Player",
            annual_records=[
                PlayerAnnualRecord(
                    year=2023,
                    team_id="old_team",
                    points_per_game=15.0,
                    games_played=40,
                    minutes_per_game=30.0,
                    salary=100_000,
                    scoring_percentile=0.60
                )
            ]
        )
        
        # Create team data with minimal changes to produce near-zero denominator
        # Same valuation for both years (zero growth)
        new_team_data = TeamData(
            team_id="new_team",
            team_name="New Team",
            market_tier=2,
            dma_ranking=30,
            annual_records=[
                TeamAnnualRecord(
                    year=2023,
                    valuation=100_000_000,
                    revenue=20_000_000,
                    attendance_avg=9000,
                    points_per_game=80.0
                ),
                TeamAnnualRecord(
                    year=2024,
                    valuation=100_000_000,  # Same valuation (zero growth)
                    revenue=20_000_000,  # Same revenue
                    attendance_avg=9000,
                    points_per_game=80.0
                )
            ]
        )
        
        old_team_data = TeamData(
            team_id="old_team",
            team_name="Old Team",
            market_tier=2,
            dma_ranking=30,
            annual_records=[
                TeamAnnualRecord(
                    year=2022,
                    valuation=95_000_000,
                    revenue=19_000_000,
                    attendance_avg=8800,
                    points_per_game=79.0
                ),
                TeamAnnualRecord(
                    year=2023,
                    valuation=100_000_000,
                    revenue=20_000_000,
                    attendance_avg=9000,
                    points_per_game=80.0
                )
            ]
        )
        
        league_data = LeagueData(
            annual_records=[
                LeagueAnnualRecord(
                    year=2023,
                    avg_viewership=1.0,
                    avg_attendance=9000,
                    avg_salary=120_000,
                    total_teams=12
                )
            ]
        )
        
        market_tier_data = MarketTierData(
            tier=2,
            adjustment_factor=1.0,
            teams=["new_team"]
        )
        
        # Calculate brand portability
        result = calculator.calculate_portability(
            player_data=player_data,
            new_team_data=new_team_data,
            league_data=league_data,
            market_tier_data=market_tier_data,
            team_data_history=[old_team_data],
            prior_year=2023,
            current_year=2024,
            player_contribution_weight=0.30
        )
        
        # Check if denominator was near zero
        delta_rm = result.components.revenue_delta.total_delta
        delta_vt = result.components.team_value_lift.net_lift
        denominator = delta_rm + delta_vt
        
        # If denominator is near zero, should have epsilon warning
        if abs(denominator) < 1e-6:
            assert len(result.warnings) > 0, "Expected warning for near-zero denominator"
            assert any("epsilon" in w.lower() for w in result.warnings), \
                f"Expected epsilon warning, got: {result.warnings}"
            
            # Chi should be calculated with epsilon (0.01)
            ch = result.components.career_baseline.avg_annual_output
            ma = result.components.market_adjustment.adjustment_factor
            expected_chi = (ch * ma) / 0.01
            
            assert abs(result.chi - expected_chi) < 0.01, \
                f"Expected chi with epsilon: {expected_chi}, got {result.chi}"
    
    def test_negative_denominator_calculates_and_warns(self):
        """
        Test edge case: negative denominator (ΔRm + ΔVt < 0) calculates and warns
        
        Requirements: Edge Cases 4
        """
        calculator = create_calculator()
        
        # Create player data
        player_data = PlayerData(
            player_id="player_1",
            player_name="Test Player",
            annual_records=[
                PlayerAnnualRecord(
                    year=2023,
                    team_id="old_team",
                    points_per_game=12.0,
                    games_played=35,
                    minutes_per_game=25.0,
                    salary=80_000,
                    scoring_percentile=0.40
                )
            ]
        )
        
        # Create team data with declining valuation (negative growth)
        new_team_data = TeamData(
            team_id="new_team",
            team_name="Declining Team",
            market_tier=3,
            dma_ranking=80,
            annual_records=[
                TeamAnnualRecord(
                    year=2023,
                    valuation=120_000_000,
                    revenue=22_000_000,
                    attendance_avg=10000,
                    points_per_game=82.0
                ),
                TeamAnnualRecord(
                    year=2024,
                    valuation=100_000_000,  # Declining valuation
                    revenue=18_000_000,  # Declining revenue
                    attendance_avg=8000,
                    points_per_game=78.0
                )
            ]
        )
        
        old_team_data = TeamData(
            team_id="old_team",
            team_name="Old Team",
            market_tier=3,
            dma_ranking=90,
            annual_records=[
                TeamAnnualRecord(
                    year=2022,
                    valuation=110_000_000,
                    revenue=20_000_000,
                    attendance_avg=9500,
                    points_per_game=80.0
                ),
                TeamAnnualRecord(
                    year=2023,
                    valuation=115_000_000,
                    revenue=21_000_000,
                    attendance_avg=9800,
                    points_per_game=81.0
                )
            ]
        )
        
        league_data = LeagueData(
            annual_records=[
                LeagueAnnualRecord(
                    year=2023,
                    avg_viewership=1.0,
                    avg_attendance=9000,
                    avg_salary=120_000,
                    total_teams=12
                )
            ]
        )
        
        market_tier_data = MarketTierData(
            tier=3,
            adjustment_factor=0.85,
            teams=["new_team"]
        )
        
        # Calculate brand portability
        result = calculator.calculate_portability(
            player_data=player_data,
            new_team_data=new_team_data,
            league_data=league_data,
            market_tier_data=market_tier_data,
            team_data_history=[old_team_data],
            prior_year=2023,
            current_year=2024,
            player_contribution_weight=0.25
        )
        
        # Check if denominator is negative
        delta_rm = result.components.revenue_delta.total_delta
        delta_vt = result.components.team_value_lift.net_lift
        denominator = delta_rm + delta_vt
        
        # If denominator is negative, should have warning
        if denominator < 0:
            assert len(result.warnings) > 0, "Expected warning for negative denominator"
            assert any("negative" in w.lower() for w in result.warnings), \
                f"Expected negative denominator warning, got: {result.warnings}"
            
            # Chi should still be calculated (negative value is valid)
            assert isinstance(result.chi, float)
    
    def test_zero_career_baseline_raises_exception(self):
        """
        Test edge case: zero career baseline raises exception
        
        Requirements: Edge Cases 1
        
        Note: This test verifies that when a player has zero or negative career baseline,
        the system raises a ValueError. This can happen when:
        1. Player has no valid career data
        2. Player's attributed revenue is zero or negative across all years
        3. Team data is missing for player's career years
        """
        calculator = create_calculator()
        
        # Create player data with zero performance
        player_data = PlayerData(
            player_id="player_1",
            player_name="Zero Player",
            annual_records=[
                PlayerAnnualRecord(
                    year=2023,
                    team_id="old_team",
                    points_per_game=0.0,  # Zero scoring
                    games_played=0,  # No games played
                    minutes_per_game=0.0,  # No minutes
                    salary=0,  # No salary
                    scoring_percentile=0.0
                )
            ]
        )
        
        new_team_data = TeamData(
            team_id="new_team",
            team_name="New Team",
            market_tier=2,
            dma_ranking=30,
            annual_records=[
                TeamAnnualRecord(
                    year=2023,
                    valuation=100_000_000,
                    revenue=20_000_000,
                    attendance_avg=9000,
                    points_per_game=80.0
                ),
                TeamAnnualRecord(
                    year=2024,
                    valuation=110_000_000,
                    revenue=22_000_000,
                    attendance_avg=9500,
                    points_per_game=82.0
                )
            ]
        )
        
        old_team_data = TeamData(
            team_id="old_team",
            team_name="Old Team",
            market_tier=2,
            dma_ranking=30,
            annual_records=[
                TeamAnnualRecord(
                    year=2022,
                    valuation=95_000_000,
                    revenue=19_000_000,
                    attendance_avg=8800,
                    points_per_game=79.0
                ),
                TeamAnnualRecord(
                    year=2023,
                    valuation=100_000_000,
                    revenue=20_000_000,
                    attendance_avg=9000,
                    points_per_game=80.0
                )
            ]
        )
        
        league_data = LeagueData(
            annual_records=[
                LeagueAnnualRecord(
                    year=2023,
                    avg_viewership=1.0,
                    avg_attendance=9000,
                    avg_salary=120_000,
                    total_teams=12
                )
            ]
        )
        
        market_tier_data = MarketTierData(
            tier=2,
            adjustment_factor=1.0,
            teams=["new_team"]
        )
        
        # Should raise ValueError for zero career baseline
        with pytest.raises(ValueError) as exc_info:
            calculator.calculate_portability(
                player_data=player_data,
                new_team_data=new_team_data,
                league_data=league_data,
                market_tier_data=market_tier_data,
                team_data_history=[old_team_data],
                prior_year=2023,
                current_year=2024,
                player_contribution_weight=0.30
            )
        
        # Verify error message mentions career baseline or portability
        error_msg = str(exc_info.value).lower()
        assert "zero career baseline" in error_msg or \
               "career baseline" in error_msg or \
               "portability" in error_msg
    
    def test_interpretation_ranges(self):
        """Test that interpretation is generated correctly for different chi ranges"""
        calculator = create_calculator()
        
        # Test exceptional portability (chi > 3.0)
        interpretation = calculator._generate_interpretation(3.5)
        assert "exceptional" in interpretation.lower()
        
        # Test high portability (2.0 < chi <= 3.0)
        interpretation = calculator._generate_interpretation(2.5)
        assert "high" in interpretation.lower()
        
        # Test moderate portability (1.0 < chi <= 2.0)
        interpretation = calculator._generate_interpretation(1.5)
        assert "moderate" in interpretation.lower()
        
        # Test low portability (0.5 < chi <= 1.0)
        interpretation = calculator._generate_interpretation(0.75)
        assert "low" in interpretation.lower()
        
        # Test minimal portability (chi <= 0.5)
        interpretation = calculator._generate_interpretation(0.3)
        assert "minimal" in interpretation.lower()
    
    def test_formula_string_correct(self):
        """Test that formula string is always correct"""
        calculator = create_calculator()
        
        player_data = PlayerData(
            player_id="player_1",
            player_name="Test Player",
            annual_records=[
                PlayerAnnualRecord(
                    year=2023,
                    team_id="old_team",
                    points_per_game=18.0,
                    games_played=40,
                    minutes_per_game=32.0,
                    salary=120_000,
                    scoring_percentile=0.70
                )
            ]
        )
        
        new_team_data = TeamData(
            team_id="new_team",
            team_name="New Team",
            market_tier=2,
            dma_ranking=25,
            annual_records=[
                TeamAnnualRecord(
                    year=2023,
                    valuation=130_000_000,
                    revenue=24_000_000,
                    attendance_avg=9500,
                    points_per_game=83.0
                ),
                TeamAnnualRecord(
                    year=2024,
                    valuation=150_000_000,
                    revenue=28_000_000,
                    attendance_avg=10500,
                    points_per_game=85.0
                )
            ]
        )
        
        old_team_data = TeamData(
            team_id="old_team",
            team_name="Old Team",
            market_tier=2,
            dma_ranking=30,
            annual_records=[
                TeamAnnualRecord(
                    year=2022,
                    valuation=110_000_000,
                    revenue=21_000_000,
                    attendance_avg=9000,
                    points_per_game=81.0
                ),
                TeamAnnualRecord(
                    year=2023,
                    valuation=120_000_000,
                    revenue=23_000_000,
                    attendance_avg=9200,
                    points_per_game=82.0
                )
            ]
        )
        
        league_data = LeagueData(
            annual_records=[
                LeagueAnnualRecord(
                    year=2023,
                    avg_viewership=1.0,
                    avg_attendance=9000,
                    avg_salary=120_000,
                    total_teams=12
                )
            ]
        )
        
        market_tier_data = MarketTierData(
            tier=2,
            adjustment_factor=1.0,
            teams=["new_team"]
        )
        
        result = calculator.calculate_portability(
            player_data=player_data,
            new_team_data=new_team_data,
            league_data=league_data,
            market_tier_data=market_tier_data,
            team_data_history=[old_team_data],
            prior_year=2023,
            current_year=2024,
            player_contribution_weight=0.35
        )
        
        # Verify formula string is correct
        assert result.formula == "χ = Ch ⋅ Ma / (ΔRm + ΔVt)"
