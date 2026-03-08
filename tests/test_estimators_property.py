"""Property-based tests for estimation layer

Feature: brand-portability-formula
Properties: 6, 7, 8, 9
"""
import pytest
from hypothesis import given, strategies as st, settings

from src.estimators import (
    MerchandiseEstimator,
    TVRatingEstimator,
    TicketPremiumEstimator,
    PlayerRevenueAttributor
)


# Strategies for valid input ranges
percentiles = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
market_tier_factors = st.sampled_from([0.85, 1.0, 1.25])
positive_floats = st.floats(min_value=0.01, max_value=1e9, allow_nan=False, allow_infinity=False)
market_reach_factors = st.floats(min_value=0.5, max_value=1.5, allow_nan=False, allow_infinity=False)
star_power_multipliers = st.floats(min_value=0.5, max_value=2.0, allow_nan=False, allow_infinity=False)
positive_integers = st.integers(min_value=1, max_value=100)


class TestMerchandiseEstimatorProperty:
    """Property-based tests for MerchandiseEstimator"""
    
    # Feature: brand-portability-formula, Property 6: Merchandise sales estimation formula
    @given(
        scoring_percentile=percentiles,
        salary_percentile=percentiles,
        market_tier_factor=market_tier_factors,
        league_revenue_baseline=positive_floats
    )
    @settings(max_examples=100, deadline=None)
    def test_merchandise_sales_formula(
        self,
        scoring_percentile,
        salary_percentile,
        market_tier_factor,
        league_revenue_baseline
    ):
        """
        Property 6: Merchandise sales estimation formula
        
        For any valid scoring percentile, salary percentile, market tier factor,
        and league revenue baseline, the estimated merchandise sales should equal
        (scoring percentile × salary percentile × market tier factor × league revenue baseline × 0.05).
        
        Validates: Requirements - Estimation Methods 1
        """
        estimator = MerchandiseEstimator()
        
        result = estimator.estimate_sales(
            scoring_percentile,
            salary_percentile,
            market_tier_factor,
            league_revenue_baseline
        )
        
        # Verify formula correctness
        expected = (
            scoring_percentile *
            salary_percentile *
            market_tier_factor *
            league_revenue_baseline *
            0.05
        )
        
        # Allow small floating point error
        assert abs(result - expected) < 0.01, \
            f"Formula mismatch: expected {expected}, got {result}"
    
    @given(
        scoring_percentile=percentiles,
        salary_percentile=percentiles,
        market_tier_factor=market_tier_factors,
        league_revenue_baseline=positive_floats
    )
    @settings(max_examples=100, deadline=None)
    def test_merchandise_sales_non_negative(
        self,
        scoring_percentile,
        salary_percentile,
        market_tier_factor,
        league_revenue_baseline
    ):
        """
        Property: Merchandise sales are always non-negative
        
        For any valid inputs, the result should be non-negative.
        """
        estimator = MerchandiseEstimator()
        
        result = estimator.estimate_sales(
            scoring_percentile,
            salary_percentile,
            market_tier_factor,
            league_revenue_baseline
        )
        
        assert result >= 0, f"Merchandise sales should be non-negative, got {result}"


class TestTVRatingEstimatorProperty:
    """Property-based tests for TVRatingEstimator"""
    
    # Feature: brand-portability-formula, Property 8: TV rating impact estimation formula
    @given(
        scoring_percentile=percentiles,
        salary_percentile=percentiles,
        social_media_index=percentiles,
        league_viewership_growth=st.floats(min_value=-1.0, max_value=5.0, allow_nan=False, allow_infinity=False),
        market_reach_factor=market_reach_factors
    )
    @settings(max_examples=100, deadline=None)
    def test_tv_rating_impact_formula(
        self,
        scoring_percentile,
        salary_percentile,
        social_media_index,
        league_viewership_growth,
        market_reach_factor
    ):
        """
        Property 8: TV rating impact estimation formula
        
        For any valid inputs, the TV rating impact should equal
        (star power score) × (league viewership growth) × (market reach factor),
        where star power score = (scoring percentile × 0.4) + (salary percentile × 0.3) + (social media index × 0.3).
        
        Validates: Requirements - Estimation Methods 3
        """
        estimator = TVRatingEstimator()
        
        result = estimator.estimate_impact(
            scoring_percentile,
            salary_percentile,
            social_media_index,
            league_viewership_growth,
            market_reach_factor
        )
        
        # Calculate expected star power
        star_power = (
            (scoring_percentile * 0.4) +
            (salary_percentile * 0.3) +
            (social_media_index * 0.3)
        )
        
        # Calculate expected impact
        expected = star_power * league_viewership_growth * market_reach_factor
        
        # Allow small floating point error
        assert abs(result - expected) < 0.001, \
            f"Formula mismatch: expected {expected}, got {result}"
    
    @given(
        scoring_percentile=percentiles,
        salary_percentile=percentiles,
        social_media_index=percentiles
    )
    @settings(max_examples=100, deadline=None)
    def test_star_power_bounds(
        self,
        scoring_percentile,
        salary_percentile,
        social_media_index
    ):
        """
        Property: Star power score is bounded between 0 and 1
        
        Since all inputs are percentiles (0-1) and weights sum to 1.0,
        star power should always be between 0 and 1.
        """
        estimator = TVRatingEstimator()
        
        # Use neutral growth and reach factors
        result = estimator.estimate_impact(
            scoring_percentile,
            salary_percentile,
            social_media_index,
            1.0,  # No growth
            1.0   # Neutral market
        )
        
        # Result should equal star power (since growth=1.0, reach=1.0)
        assert 0.0 <= result <= 1.0, f"Star power should be in [0,1], got {result}"


class TestTicketPremiumEstimatorProperty:
    """Property-based tests for TicketPremiumEstimator"""
    
    # Feature: brand-portability-formula, Property 9: Ticket premium estimation formula
    @given(
        attendance_with_player=st.floats(min_value=0, max_value=20000, allow_nan=False, allow_infinity=False),
        attendance_without_player=st.floats(min_value=0, max_value=20000, allow_nan=False, allow_infinity=False),
        avg_ticket_price=positive_floats,
        player_performance_weight=percentiles,
        star_power_multiplier=star_power_multipliers,
        home_games=positive_integers
    )
    @settings(max_examples=100, deadline=None)
    def test_ticket_premium_formula(
        self,
        attendance_with_player,
        attendance_without_player,
        avg_ticket_price,
        player_performance_weight,
        star_power_multiplier,
        home_games
    ):
        """
        Property 9: Ticket premium estimation formula
        
        For any valid attendance differential, average ticket price, attribution factor,
        and number of home games, the ticket premium should equal
        (attendance differential) × (average ticket price) × (attribution factor) × (home games).
        
        Validates: Requirements - Estimation Methods 4
        """
        estimator = TicketPremiumEstimator()
        
        result = estimator.estimate_premium(
            attendance_with_player,
            attendance_without_player,
            avg_ticket_price,
            player_performance_weight,
            star_power_multiplier,
            home_games
        )
        
        # Calculate expected values
        attendance_diff = attendance_with_player - attendance_without_player
        attribution_factor = player_performance_weight * star_power_multiplier
        expected = attendance_diff * avg_ticket_price * attribution_factor * home_games
        
        # Allow small floating point error
        assert abs(result - expected) < 1.0, \
            f"Formula mismatch: expected {expected}, got {result}"
    
    @given(
        attendance=st.floats(min_value=0, max_value=20000, allow_nan=False, allow_infinity=False),
        avg_ticket_price=positive_floats,
        player_performance_weight=percentiles,
        star_power_multiplier=star_power_multipliers,
        home_games=positive_integers
    )
    @settings(max_examples=100, deadline=None)
    def test_ticket_premium_zero_when_no_change(
        self,
        attendance,
        avg_ticket_price,
        player_performance_weight,
        star_power_multiplier,
        home_games
    ):
        """
        Property: Ticket premium is zero when attendance doesn't change
        
        When attendance with and without player are equal, premium should be zero.
        """
        estimator = TicketPremiumEstimator()
        
        result = estimator.estimate_premium(
            attendance,
            attendance,  # Same attendance
            avg_ticket_price,
            player_performance_weight,
            star_power_multiplier,
            home_games
        )
        
        assert abs(result) < 0.01, f"Premium should be zero when attendance unchanged, got {result}"


class TestPlayerRevenueAttributorProperty:
    """Property-based tests for PlayerRevenueAttributor"""
    
    # Feature: brand-portability-formula, Property 7: Player revenue attribution formula
    @given(
        team_revenue_change=st.floats(min_value=-1e9, max_value=1e9, allow_nan=False, allow_infinity=False),
        player_ppg=st.floats(min_value=0, max_value=40, allow_nan=False, allow_infinity=False),
        team_ppg=st.floats(min_value=50, max_value=120, allow_nan=False, allow_infinity=False),
        player_salary=st.floats(min_value=0, max_value=500_000, allow_nan=False, allow_infinity=False),
        team_salary_cap=st.floats(min_value=1_000_000, max_value=2_000_000, allow_nan=False, allow_infinity=False),
        games_played=st.integers(min_value=0, max_value=40),
        total_games=st.integers(min_value=40, max_value=40),
        minutes_per_game=st.floats(min_value=0, max_value=40, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_player_revenue_attribution_formula(
        self,
        team_revenue_change,
        player_ppg,
        team_ppg,
        player_salary,
        team_salary_cap,
        games_played,
        total_games,
        minutes_per_game
    ):
        """
        Property 7: Player revenue attribution formula
        
        For any valid team revenue change, player performance metrics, and playing time data,
        the attributed player revenue impact should equal
        (team revenue change) × (performance weight) × (playing time percentage),
        where performance weight = (player PPG / team PPG) × 0.6 + (player salary / team salary cap) × 0.4.
        
        Validates: Requirements - Estimation Methods 2
        """
        attributor = PlayerRevenueAttributor()
        
        result = attributor.calculate_attribution(
            team_revenue_change,
            player_ppg,
            team_ppg,
            player_salary,
            team_salary_cap,
            games_played,
            total_games,
            minutes_per_game
        )
        
        # Calculate expected values
        performance_weight = (player_ppg / team_ppg) * 0.6 + (player_salary / team_salary_cap) * 0.4
        playing_time_pct = (games_played / total_games) * (minutes_per_game / 40)
        expected = team_revenue_change * performance_weight * playing_time_pct
        
        # Allow small floating point error
        assert abs(result - expected) < 1000.0, \
            f"Formula mismatch: expected {expected}, got {result}"
    
    @given(
        player_ppg=st.floats(min_value=0, max_value=40, allow_nan=False, allow_infinity=False),
        team_ppg=st.floats(min_value=50, max_value=120, allow_nan=False, allow_infinity=False),
        player_salary=st.floats(min_value=0, max_value=500_000, allow_nan=False, allow_infinity=False),
        team_salary_cap=st.floats(min_value=1_000_000, max_value=2_000_000, allow_nan=False, allow_infinity=False),
        games_played=st.integers(min_value=0, max_value=40),
        total_games=st.integers(min_value=40, max_value=40),
        minutes_per_game=st.floats(min_value=0, max_value=40, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_attribution_zero_when_no_revenue_change(
        self,
        player_ppg,
        team_ppg,
        player_salary,
        team_salary_cap,
        games_played,
        total_games,
        minutes_per_game
    ):
        """
        Property: Attribution is zero when team revenue doesn't change
        
        When team revenue change is zero, attributed impact should be zero.
        """
        attributor = PlayerRevenueAttributor()
        
        result = attributor.calculate_attribution(
            0,  # No revenue change
            player_ppg,
            team_ppg,
            player_salary,
            team_salary_cap,
            games_played,
            total_games,
            minutes_per_game
        )
        
        assert abs(result) < 0.01, f"Attribution should be zero when no revenue change, got {result}"
