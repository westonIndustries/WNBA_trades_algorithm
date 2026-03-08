"""Property-based tests for Career Baseline Calculator"""
import pytest
from hypothesis import given, strategies as st, assume

from src.calculators import CareerBaselineCalculator
from src.estimators import PlayerRevenueAttributor
from src.models import PlayerData, PlayerAnnualRecord, TeamData, TeamAnnualRecord


# Feature: brand-portability-formula, Property 4: Career baseline calculation
# Validates: Requirements - Ch Definition
@given(
    num_years=st.integers(min_value=1, max_value=5),
    base_ppg=st.floats(min_value=10.0, max_value=25.0, allow_nan=False, allow_infinity=False),
    base_salary=st.floats(min_value=60_000, max_value=200_000, allow_nan=False, allow_infinity=False),
    base_revenue_change=st.floats(min_value=1_000_000, max_value=10_000_000, allow_nan=False, allow_infinity=False)
)
def test_career_baseline_equals_arithmetic_mean(num_years, base_ppg, base_salary, base_revenue_change):
    """
    Property 4: Career baseline calculation
    
    For any player with multiple years of career data, the career baseline (Ch)
    should equal the arithmetic mean of all annual commercial outputs.
    
    **Validates: Requirements - Ch Definition**
    """
    # Create player data with annual records
    player_records = []
    for i in range(num_years):
        year = 2020 + i
        player_records.append(
            PlayerAnnualRecord(
                year=year,
                team_id="TEAM1",
                points_per_game=base_ppg,
                games_played=40,
                minutes_per_game=35.0,
                salary=base_salary
            )
        )
    
    player_data = PlayerData(
        player_id="P1",
        player_name="Test Player",
        annual_records=player_records
    )
    
    # Create team data with consistent revenue changes
    team_records = []
    for i in range(num_years):
        year = 2020 + i
        # Create current year record
        team_records.append(
            TeamAnnualRecord(
                year=year,
                valuation=100_000_000,
                revenue=10_000_000 + base_revenue_change,
                attendance_avg=10000,
                points_per_game=80.0
            )
        )
        
        # Create prior year record
        team_records.append(
            TeamAnnualRecord(
                year=year - 1,
                valuation=95_000_000,
                revenue=10_000_000,
                attendance_avg=9500,
                points_per_game=78.0
            )
        )
    
    team_data = TeamData(
        team_id="TEAM1",
        team_name="Test Team",
        market_tier=2,
        dma_ranking=25,
        annual_records=team_records
    )
    
    # Create calculator
    revenue_attributor = PlayerRevenueAttributor()
    calculator = CareerBaselineCalculator(revenue_attributor)
    
    # Calculate career baseline
    result = calculator.calculate(player_data, [team_data])
    
    # Verify the result structure
    assert result.total_years == num_years, (
        f"Total years {result.total_years} should equal {num_years}"
    )
    
    assert len(result.annual_breakdown) == num_years, (
        f"Annual breakdown length {len(result.annual_breakdown)} should equal {num_years}"
    )
    
    # Calculate expected mean from actual annual outputs
    total_output = sum(output for _, output in result.annual_breakdown)
    expected_mean = total_output / num_years
    
    # Verify the average equals the arithmetic mean of annual outputs
    assert abs(result.avg_annual_output - expected_mean) < 0.01, (
        f"Career baseline {result.avg_annual_output} should equal "
        f"arithmetic mean {expected_mean}"
    )
    
    # Verify career baseline is positive
    assert result.avg_annual_output > 0, (
        f"Career baseline should be positive, got {result.avg_annual_output}"
    )


# Feature: brand-portability-formula, Property 4: Career baseline calculation (simplified)
# Validates: Requirements - Ch Definition
@given(
    num_years=st.integers(min_value=1, max_value=5),
    base_revenue_change=st.floats(min_value=100_000, max_value=5_000_000, allow_nan=False, allow_infinity=False)
)
def test_career_baseline_calculation_structure(num_years, base_revenue_change):
    """
    Property 4: Career baseline calculation (structure validation)
    
    For any player with career data, the career baseline calculation should:
    1. Return a positive average annual output (if data is valid)
    2. Have total_years equal to the number of valid years
    3. Have annual_breakdown with one entry per year
    
    **Validates: Requirements - Ch Definition**
    """
    # Create player data
    player_records = []
    for i in range(num_years):
        year = 2020 + i
        player_records.append(
            PlayerAnnualRecord(
                year=year,
                team_id="TEAM1",
                points_per_game=15.0,
                games_played=40,
                minutes_per_game=30.0,
                salary=100_000
            )
        )
    
    player_data = PlayerData(
        player_id="P1",
        player_name="Test Player",
        annual_records=player_records
    )
    
    # Create team data
    team_records = []
    for i in range(num_years):
        year = 2020 + i
        team_records.append(
            TeamAnnualRecord(
                year=year,
                valuation=100_000_000,
                revenue=10_000_000 + base_revenue_change,
                attendance_avg=10000,
                points_per_game=80.0
            )
        )
        team_records.append(
            TeamAnnualRecord(
                year=year - 1,
                valuation=95_000_000,
                revenue=10_000_000,
                attendance_avg=9500,
                points_per_game=78.0
            )
        )
    
    team_data = TeamData(
        team_id="TEAM1",
        team_name="Test Team",
        market_tier=2,
        dma_ranking=25,
        annual_records=team_records
    )
    
    # Create calculator
    revenue_attributor = PlayerRevenueAttributor()
    calculator = CareerBaselineCalculator(revenue_attributor)
    
    # Calculate career baseline
    result = calculator.calculate(player_data, [team_data])
    
    # Property 1: Average annual output should be positive
    assert result.avg_annual_output > 0, (
        f"Average annual output should be positive, got {result.avg_annual_output}"
    )
    
    # Property 2: Total years should match input
    assert result.total_years == num_years, (
        f"Total years {result.total_years} should equal {num_years}"
    )
    
    # Property 3: Annual breakdown should have one entry per year
    assert len(result.annual_breakdown) == num_years, (
        f"Annual breakdown should have {num_years} entries, got {len(result.annual_breakdown)}"
    )
    
    # Property 4: Each annual output should be non-negative
    for year, output in result.annual_breakdown:
        assert output >= 0, f"Annual output for year {year} should be non-negative, got {output}"
    
    # Property 5: Sum of annual outputs divided by years should equal average
    total_output = sum(output for _, output in result.annual_breakdown)
    calculated_avg = total_output / num_years
    assert abs(result.avg_annual_output - calculated_avg) < 0.01, (
        f"Average {result.avg_annual_output} should equal calculated average {calculated_avg}"
    )



# Feature: brand-portability-formula, Property 11: Non-negative career baseline
# Validates: Requirements - Ch Definition, Edge Cases
@given(
    num_years=st.integers(min_value=1, max_value=5),
    player_ppg=st.floats(min_value=5.0, max_value=30.0, allow_nan=False, allow_infinity=False),
    player_salary=st.floats(min_value=50_000, max_value=250_000, allow_nan=False, allow_infinity=False),
    games_played=st.integers(min_value=1, max_value=40),
    minutes_per_game=st.floats(min_value=10.0, max_value=40.0, allow_nan=False, allow_infinity=False),
    team_revenue_change=st.floats(min_value=100_000, max_value=10_000_000, allow_nan=False, allow_infinity=False)
)
def test_career_baseline_always_non_negative(
    num_years,
    player_ppg,
    player_salary,
    games_played,
    minutes_per_game,
    team_revenue_change
):
    """
    Property 11: Non-negative career baseline
    
    For any player with valid career data (positive annual outputs), the career
    baseline (Ch) should always be greater than zero.
    
    **Validates: Requirements - Ch Definition, Edge Cases**
    """
    # Create player data with positive performance metrics
    player_records = []
    for i in range(num_years):
        year = 2020 + i
        player_records.append(
            PlayerAnnualRecord(
                year=year,
                team_id="TEAM1",
                points_per_game=player_ppg,
                games_played=games_played,
                minutes_per_game=minutes_per_game,
                salary=player_salary
            )
        )
    
    player_data = PlayerData(
        player_id="P1",
        player_name="Test Player",
        annual_records=player_records
    )
    
    # Create team data with positive revenue changes
    team_records = []
    for i in range(num_years):
        year = 2020 + i
        team_records.append(
            TeamAnnualRecord(
                year=year,
                valuation=100_000_000,
                revenue=10_000_000 + team_revenue_change,
                attendance_avg=10000,
                points_per_game=80.0
            )
        )
        team_records.append(
            TeamAnnualRecord(
                year=year - 1,
                valuation=95_000_000,
                revenue=10_000_000,
                attendance_avg=9500,
                points_per_game=78.0
            )
        )
    
    team_data = TeamData(
        team_id="TEAM1",
        team_name="Test Team",
        market_tier=2,
        dma_ranking=25,
        annual_records=team_records
    )
    
    # Create calculator
    revenue_attributor = PlayerRevenueAttributor()
    calculator = CareerBaselineCalculator(revenue_attributor)
    
    # Calculate career baseline
    result = calculator.calculate(player_data, [team_data])
    
    # Property: Career baseline should always be greater than zero
    assert result.avg_annual_output > 0, (
        f"Career baseline should be positive, got {result.avg_annual_output}"
    )
    
    # Additional property: All annual outputs should be non-negative
    for year, output in result.annual_breakdown:
        assert output >= 0, (
            f"Annual output for year {year} should be non-negative, got {output}"
        )


# Feature: brand-portability-formula, Property 11: Non-negative career baseline (edge case)
# Validates: Requirements - Ch Definition, Edge Cases
def test_zero_career_baseline_raises_exception():
    """
    Property 11: Non-negative career baseline (edge case)
    
    When a player has zero career baseline (no measurable commercial output),
    the calculator should raise a ValueError.
    
    **Validates: Requirements - Ch Definition, Edge Cases**
    """
    # Create player data with zero performance
    player_records = [
        PlayerAnnualRecord(
            year=2020,
            team_id="TEAM1",
            points_per_game=0.0,
            games_played=0,
            minutes_per_game=0.0,
            salary=0.0
        )
    ]
    
    player_data = PlayerData(
        player_id="P1",
        player_name="Test Player",
        annual_records=player_records
    )
    
    # Create team data
    team_records = [
        TeamAnnualRecord(
            year=2020,
            valuation=100_000_000,
            revenue=10_000_000,
            attendance_avg=10000,
            points_per_game=80.0
        ),
        TeamAnnualRecord(
            year=2019,
            valuation=95_000_000,
            revenue=10_000_000,
            attendance_avg=9500,
            points_per_game=78.0
        )
    ]
    
    team_data = TeamData(
        team_id="TEAM1",
        team_name="Test Team",
        market_tier=2,
        dma_ranking=25,
        annual_records=team_records
    )
    
    # Create calculator
    revenue_attributor = PlayerRevenueAttributor()
    calculator = CareerBaselineCalculator(revenue_attributor)
    
    # Should raise ValueError for zero career baseline
    with pytest.raises(ValueError, match="zero career baseline"):
        calculator.calculate(player_data, [team_data])
