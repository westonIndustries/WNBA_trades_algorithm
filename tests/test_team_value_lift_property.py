"""Property-based tests for TeamValueLiftCalculator

Feature: brand-portability-formula
Properties: 3, 10
"""
import pytest
from hypothesis import given, strategies as st, settings, assume

from src.calculators import TeamValueLiftCalculator
from src.models import TeamData, TeamAnnualRecord, LeagueData, LeagueAnnualRecord


# Strategies for generating valid test data
positive_valuations = st.floats(min_value=10_000_000, max_value=500_000_000, allow_nan=False, allow_infinity=False)
positive_revenues = st.floats(min_value=1_000_000, max_value=100_000_000, allow_nan=False, allow_infinity=False)
positive_salaries = st.floats(min_value=50_000, max_value=300_000, allow_nan=False, allow_infinity=False)
years = st.integers(min_value=2020, max_value=2030)


class TestTeamValueLiftCalculatorProperty:
    """Property-based tests for TeamValueLiftCalculator"""
    
    # Feature: brand-portability-formula, Property 3: Team value lift calculation
    @given(
        prior_valuation=positive_valuations,
        current_valuation=positive_valuations,
        prior_salary=positive_salaries,
        current_salary=positive_salaries,
        year=years
    )
    @settings(max_examples=100, deadline=None)
    def test_team_value_lift_calculation(
        self,
        prior_valuation,
        current_valuation,
        prior_salary,
        current_salary,
        year
    ):
        """
        Property 3: Team value lift calculation
        
        For any team with valuation history and league data, the team value lift (ΔVt)
        should equal the team's growth rate minus the league average growth rate.
        
        Validates: Requirements - ΔVt Definition
        """
        calculator = TeamValueLiftCalculator()
        
        # Create team data
        team_data = TeamData(
            team_id="test_team",
            team_name="Test Team",
            market_tier=2,
            dma_ranking=15,
            annual_records=[
                TeamAnnualRecord(
                    year=year,
                    valuation=prior_valuation,
                    revenue=10_000_000,
                    attendance_avg=9000,
                    points_per_game=82.0
                ),
                TeamAnnualRecord(
                    year=year + 1,
                    valuation=current_valuation,
                    revenue=12_000_000,
                    attendance_avg=9500,
                    points_per_game=84.0
                )
            ]
        )
        
        # Create league data
        league_data = LeagueData(
            annual_records=[
                LeagueAnnualRecord(
                    year=year,
                    avg_viewership=1.0,
                    avg_attendance=9000,
                    avg_salary=prior_salary,
                    total_teams=12
                ),
                LeagueAnnualRecord(
                    year=year + 1,
                    avg_viewership=1.1,
                    avg_attendance=9200,
                    avg_salary=current_salary,
                    total_teams=12
                )
            ]
        )
        
        # Calculate team value lift
        result = calculator.calculate(team_data, league_data, year, year + 1)
        
        # Verify formula: ΔVt = Team Growth Rate - League Average Growth Rate
        expected_team_growth = (current_valuation - prior_valuation) / prior_valuation
        expected_net_lift = expected_team_growth - result.league_avg_growth_rate
        
        # Allow small floating point error
        assert abs(result.team_growth_rate - expected_team_growth) < 0.001, \
            f"Team growth rate mismatch: expected {expected_team_growth}, got {result.team_growth_rate}"
        
        assert abs(result.net_lift - expected_net_lift) < 0.001, \
            f"Net lift mismatch: expected {expected_net_lift}, got {result.net_lift}"
    
    # Feature: brand-portability-formula, Property 10: League average growth rate calculation
    @given(
        prior_salary=positive_salaries,
        current_salary=positive_salaries,
        year=years
    )
    @settings(max_examples=100, deadline=None)
    def test_league_average_growth_calculation(
        self,
        prior_salary,
        current_salary,
        year
    ):
        """
        Property 10: League average growth rate calculation
        
        For any set of team valuations across two years, the league average growth rate
        should be calculated based on the change in league-wide metrics.
        
        Validates: Requirements - Estimation Methods 5
        """
        # Skip if salaries are too close (would result in near-zero growth)
        assume(abs(current_salary - prior_salary) > 1000)
        
        calculator = TeamValueLiftCalculator()
        
        # Create league data
        league_data = LeagueData(
            annual_records=[
                LeagueAnnualRecord(
                    year=year,
                    avg_viewership=1.0,
                    avg_attendance=9000,
                    avg_salary=prior_salary,
                    total_teams=12
                ),
                LeagueAnnualRecord(
                    year=year + 1,
                    avg_viewership=1.1,
                    avg_attendance=9200,
                    avg_salary=current_salary,
                    total_teams=12
                )
            ]
        )
        
        # Calculate league average growth
        growth_rate = calculator.calculate_league_avg_growth(league_data, year, year + 1)
        
        # Growth rate should be a reasonable value
        # (not NaN, not infinite, within reasonable bounds)
        assert not (growth_rate != growth_rate), "Growth rate should not be NaN"  # NaN check
        assert abs(growth_rate) <= 10.0, f"Growth rate should be reasonable, got {growth_rate}"
        
        # If salary increased, growth should be positive; if decreased, negative
        salary_change = current_salary - prior_salary
        if salary_change > 1000:
            assert growth_rate > 0, f"Growth should be positive when salary increases, got {growth_rate}"
        elif salary_change < -1000:
            assert growth_rate < 0, f"Growth should be negative when salary decreases, got {growth_rate}"
    
    @given(
        prior_valuation=positive_valuations,
        current_valuation=positive_valuations,
        year=years
    )
    @settings(max_examples=100, deadline=None)
    def test_team_growth_rate_formula(
        self,
        prior_valuation,
        current_valuation,
        year
    ):
        """
        Property: Team growth rate follows standard growth formula
        
        Team growth rate should equal (current - prior) / prior.
        """
        calculator = TeamValueLiftCalculator()
        
        team_data = TeamData(
            team_id="test_team",
            team_name="Test Team",
            market_tier=2,
            dma_ranking=15,
            annual_records=[
                TeamAnnualRecord(
                    year=year,
                    valuation=prior_valuation,
                    revenue=10_000_000,
                    attendance_avg=9000,
                    points_per_game=82.0
                ),
                TeamAnnualRecord(
                    year=year + 1,
                    valuation=current_valuation,
                    revenue=12_000_000,
                    attendance_avg=9500,
                    points_per_game=84.0
                )
            ]
        )
        
        league_data = LeagueData(
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
        
        result = calculator.calculate(team_data, league_data, year, year + 1)
        
        # Verify growth rate formula
        expected_growth = (current_valuation - prior_valuation) / prior_valuation
        assert abs(result.team_growth_rate - expected_growth) < 0.001, \
            f"Growth rate formula mismatch: expected {expected_growth}, got {result.team_growth_rate}"
    
    @given(
        valuation=positive_valuations,
        year=years
    )
    @settings(max_examples=100, deadline=None)
    def test_zero_growth_when_no_change(
        self,
        valuation,
        year
    ):
        """
        Property: Zero growth when valuation doesn't change
        
        When prior and current valuations are equal, team growth rate should be zero.
        """
        calculator = TeamValueLiftCalculator()
        
        team_data = TeamData(
            team_id="test_team",
            team_name="Test Team",
            market_tier=2,
            dma_ranking=15,
            annual_records=[
                TeamAnnualRecord(
                    year=year,
                    valuation=valuation,
                    revenue=10_000_000,
                    attendance_avg=9000,
                    points_per_game=82.0
                ),
                TeamAnnualRecord(
                    year=year + 1,
                    valuation=valuation,  # Same valuation
                    revenue=10_000_000,
                    attendance_avg=9000,
                    points_per_game=82.0
                )
            ]
        )
        
        league_data = LeagueData(
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
        
        result = calculator.calculate(team_data, league_data, year, year + 1)
        
        # Team growth rate should be zero
        assert abs(result.team_growth_rate) < 0.001, \
            f"Growth rate should be zero when valuation unchanged, got {result.team_growth_rate}"
    
    @given(
        prior_valuation=positive_valuations,
        current_valuation=positive_valuations,
        year=years
    )
    @settings(max_examples=100, deadline=None)
    def test_net_lift_components(
        self,
        prior_valuation,
        current_valuation,
        year
    ):
        """
        Property: Net lift equals team growth minus league growth
        
        The net lift should always equal team_growth_rate - league_avg_growth_rate.
        """
        calculator = TeamValueLiftCalculator()
        
        team_data = TeamData(
            team_id="test_team",
            team_name="Test Team",
            market_tier=2,
            dma_ranking=15,
            annual_records=[
                TeamAnnualRecord(
                    year=year,
                    valuation=prior_valuation,
                    revenue=10_000_000,
                    attendance_avg=9000,
                    points_per_game=82.0
                ),
                TeamAnnualRecord(
                    year=year + 1,
                    valuation=current_valuation,
                    revenue=12_000_000,
                    attendance_avg=9500,
                    points_per_game=84.0
                )
            ]
        )
        
        league_data = LeagueData(
            annual_records=[
                LeagueAnnualRecord(
                    year=year,
                    avg_viewership=1.0,
                    avg_attendance=9000,
                    avg_salary=120_000,
                    total_teams=12
                ),
                LeagueAnnualRecord(
                    year=year + 1,
                    avg_viewership=1.1,
                    avg_attendance=9200,
                    avg_salary=132_000,
                    total_teams=12
                )
            ]
        )
        
        result = calculator.calculate(team_data, league_data, year, year + 1)
        
        # Verify net lift formula
        expected_net_lift = result.team_growth_rate - result.league_avg_growth_rate
        assert abs(result.net_lift - expected_net_lift) < 0.001, \
            f"Net lift formula mismatch: expected {expected_net_lift}, got {result.net_lift}"
