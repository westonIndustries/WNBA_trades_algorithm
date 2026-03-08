"""Property-based tests for RevenueDeltaCalculator

Feature: brand-portability-formula
Properties: 2, 13
"""
import pytest
from hypothesis import given, strategies as st, settings

from src.calculators import RevenueDeltaCalculator
from src.estimators import (
    MerchandiseEstimator,
    TVRatingEstimator,
    TicketPremiumEstimator
)
from src.models import (
    PlayerData,
    PlayerAnnualRecord,
    TeamData,
    TeamAnnualRecord,
    LeagueData,
    LeagueAnnualRecord
)


# Strategies for generating valid test data
percentiles = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
positive_floats = st.floats(min_value=1.0, max_value=1e8, allow_nan=False, allow_infinity=False)
years = st.integers(min_value=2020, max_value=2030)
market_tiers = st.integers(min_value=1, max_value=3)
dma_rankings = st.integers(min_value=1, max_value=100)
games = st.integers(min_value=1, max_value=40)


def create_player_data(year: int, scoring_pct: float) -> PlayerData:
    """Helper to create player data"""
    return PlayerData(
        player_id="test_player",
        player_name="Test Player",
        annual_records=[
            PlayerAnnualRecord(
                year=year,
                team_id="old_team",
                points_per_game=20.0,
                games_played=40,
                minutes_per_game=35.0,
                salary=100_000,
                scoring_percentile=scoring_pct
            )
        ]
    )


def create_team_data(year: int, market_tier: int, dma: int, revenue: float) -> TeamData:
    """Helper to create team data"""
    return TeamData(
        team_id="new_team",
        team_name="New Team",
        market_tier=market_tier,
        dma_ranking=dma,
        annual_records=[
            TeamAnnualRecord(
                year=year,
                valuation=200_000_000,
                revenue=revenue,
                attendance_avg=10000,
                points_per_game=85.0
            )
        ]
    )


def create_league_data(year: int) -> LeagueData:
    """Helper to create league data"""
    return LeagueData(
        annual_records=[
            LeagueAnnualRecord(
                year=year,
                avg_viewership=1.0,
                avg_attendance=9000,
                avg_salary=120_000,
                total_teams=12
            )
        ]
    )


class TestRevenueDeltaCalculatorProperty:
    """Property-based tests for RevenueDeltaCalculator"""
    
    # Feature: brand-portability-formula, Property 2: Revenue delta calculation
    @given(
        year=years,
        scoring_pct=percentiles,
        market_tier=market_tiers,
        dma=dma_rankings,
        revenue=positive_floats
    )
    @settings(max_examples=100, deadline=None)
    def test_revenue_delta_calculation(
        self,
        year,
        scoring_pct,
        market_tier,
        dma,
        revenue
    ):
        """
        Property 2: Revenue delta calculation
        
        For any player with career history and any new team, the revenue delta (ΔRm)
        should equal the estimated new city revenue minus the player's career average revenue.
        
        Validates: Requirements - ΔRm Definition
        """
        # Create calculator
        merch_est = MerchandiseEstimator()
        tv_est = TVRatingEstimator()
        ticket_est = TicketPremiumEstimator()
        calculator = RevenueDeltaCalculator(merch_est, tv_est, ticket_est)
        
        # Create test data
        player_data = create_player_data(year, scoring_pct)
        team_data = create_team_data(year + 1, market_tier, dma, revenue)
        league_data = create_league_data(year)
        
        # Calculate revenue delta
        result = calculator.calculate(player_data, team_data, league_data)
        
        # Verify formula: ΔRm = New City Revenue - Career Average Revenue
        expected_delta = result.new_city_revenue - result.career_avg_revenue
        
        # Allow small floating point error
        assert abs(result.total_delta - expected_delta) < 0.01, \
            f"Revenue delta mismatch: expected {expected_delta}, got {result.total_delta}"
    
    # Feature: brand-portability-formula, Property 13: Revenue delta components sum
    @given(
        year=years,
        scoring_pct=percentiles,
        market_tier=market_tiers,
        dma=dma_rankings,
        revenue=positive_floats
    )
    @settings(max_examples=100, deadline=None)
    def test_revenue_delta_components_sum(
        self,
        year,
        scoring_pct,
        market_tier,
        dma,
        revenue
    ):
        """
        Property 13: Revenue delta components sum
        
        For any revenue delta calculation, the total delta should equal the sum of
        merchandise sales estimate, TV rating impact estimate, and ticket premium estimate
        minus the career average of these same components.
        
        Validates: Requirements - ΔRm Definition, Components
        """
        # Create calculator
        merch_est = MerchandiseEstimator()
        tv_est = TVRatingEstimator()
        ticket_est = TicketPremiumEstimator()
        calculator = RevenueDeltaCalculator(merch_est, tv_est, ticket_est)
        
        # Create test data
        player_data = create_player_data(year, scoring_pct)
        team_data = create_team_data(year + 1, market_tier, dma, revenue)
        league_data = create_league_data(year)
        
        # Calculate revenue delta
        result = calculator.calculate(player_data, team_data, league_data)
        
        # Verify components sum to total delta
        component_sum = (
            result.components["merchandise"] +
            result.components["tv_rating"] +
            result.components["ticket_premium"]
        )
        
        # Allow small floating point error
        assert abs(result.total_delta - component_sum) < 0.01, \
            f"Component sum mismatch: total_delta={result.total_delta}, component_sum={component_sum}"
    
    @given(
        year=years,
        scoring_pct=percentiles,
        market_tier=market_tiers,
        dma=dma_rankings,
        revenue=positive_floats
    )
    @settings(max_examples=100, deadline=None)
    def test_revenue_values_non_negative(
        self,
        year,
        scoring_pct,
        market_tier,
        dma,
        revenue
    ):
        """
        Property: Career average and new city revenue are non-negative
        
        Both career average revenue and new city revenue should always be non-negative
        since they represent absolute revenue values (not deltas).
        """
        # Create calculator
        merch_est = MerchandiseEstimator()
        tv_est = TVRatingEstimator()
        ticket_est = TicketPremiumEstimator()
        calculator = RevenueDeltaCalculator(merch_est, tv_est, ticket_est)
        
        # Create test data
        player_data = create_player_data(year, scoring_pct)
        team_data = create_team_data(year + 1, market_tier, dma, revenue)
        league_data = create_league_data(year)
        
        # Calculate revenue delta
        result = calculator.calculate(player_data, team_data, league_data)
        
        # Verify non-negative values
        assert result.career_avg_revenue >= 0, \
            f"Career average revenue should be non-negative, got {result.career_avg_revenue}"
        assert result.new_city_revenue >= 0, \
            f"New city revenue should be non-negative, got {result.new_city_revenue}"
    
    @given(
        year=years,
        scoring_pct=percentiles,
        market_tier=market_tiers,
        dma=dma_rankings,
        revenue=positive_floats
    )
    @settings(max_examples=100, deadline=None)
    def test_components_exist(
        self,
        year,
        scoring_pct,
        market_tier,
        dma,
        revenue
    ):
        """
        Property: All three revenue components must be present
        
        The result must include all three components: merchandise, tv_rating, ticket_premium.
        """
        # Create calculator
        merch_est = MerchandiseEstimator()
        tv_est = TVRatingEstimator()
        ticket_est = TicketPremiumEstimator()
        calculator = RevenueDeltaCalculator(merch_est, tv_est, ticket_est)
        
        # Create test data
        player_data = create_player_data(year, scoring_pct)
        team_data = create_team_data(year + 1, market_tier, dma, revenue)
        league_data = create_league_data(year)
        
        # Calculate revenue delta
        result = calculator.calculate(player_data, team_data, league_data)
        
        # Verify all components exist
        assert "merchandise" in result.components, "Missing merchandise component"
        assert "tv_rating" in result.components, "Missing tv_rating component"
        assert "ticket_premium" in result.components, "Missing ticket_premium component"
        assert len(result.components) == 3, f"Expected 3 components, got {len(result.components)}"
