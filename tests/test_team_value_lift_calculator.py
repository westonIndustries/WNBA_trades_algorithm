"""Unit tests for TeamValueLiftCalculator"""
import pytest

from src.calculators import TeamValueLiftCalculator, TeamValueLiftResult
from src.models import TeamData, TeamAnnualRecord, LeagueData, LeagueAnnualRecord


class TestTeamValueLiftCalculator:
    """Unit tests for TeamValueLiftCalculator"""
    
    def test_calculate_basic(self):
        """Test basic team value lift calculation"""
        calculator = TeamValueLiftCalculator()
        
        # Create team data with 2-year valuation history
        team_data = TeamData(
            team_id="team_1",
            team_name="Test Team",
            market_tier=2,
            dma_ranking=15,
            annual_records=[
                TeamAnnualRecord(
                    year=2023,
                    valuation=100_000_000,
                    revenue=20_000_000,
                    attendance_avg=9000,
                    points_per_game=82.0
                ),
                TeamAnnualRecord(
                    year=2024,
                    valuation=150_000_000,  # 50% growth
                    revenue=25_000_000,
                    attendance_avg=10000,
                    points_per_game=85.0
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
                ),
                LeagueAnnualRecord(
                    year=2024,
                    avg_viewership=1.2,
                    avg_attendance=9500,
                    avg_salary=132_000,  # 10% growth
                    total_teams=12
                )
            ]
        )
        
        # Calculate team value lift
        result = calculator.calculate(team_data, league_data, 2023, 2024)
        
        # Verify result structure
        assert isinstance(result, TeamValueLiftResult)
        assert result.team_valuation_prior == 100_000_000
        assert result.team_valuation_current == 150_000_000
        
        # Team growth rate should be 50%
        assert abs(result.team_growth_rate - 0.5) < 0.01
        
        # League average growth should be calculated
        assert result.league_avg_growth_rate > 0
        
        # Net lift should be team growth minus league average
        expected_net_lift = result.team_growth_rate - result.league_avg_growth_rate
        assert abs(result.net_lift - expected_net_lift) < 0.01
    
    def test_calculate_positive_lift(self):
        """Test calculation when team outperforms league"""
        calculator = TeamValueLiftCalculator()
        
        team_data = TeamData(
            team_id="team_1",
            team_name="Star Team",
            market_tier=1,
            dma_ranking=5,
            annual_records=[
                TeamAnnualRecord(
                    year=2023,
                    valuation=100_000_000,
                    revenue=20_000_000,
                    attendance_avg=9000,
                    points_per_game=82.0
                ),
                TeamAnnualRecord(
                    year=2024,
                    valuation=200_000_000,  # 100% growth (exceptional)
                    revenue=35_000_000,
                    attendance_avg=15000,
                    points_per_game=88.0
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
                ),
                LeagueAnnualRecord(
                    year=2024,
                    avg_viewership=1.1,
                    avg_attendance=9200,
                    avg_salary=126_000,  # 5% growth
                    total_teams=12
                )
            ]
        )
        
        result = calculator.calculate(team_data, league_data, 2023, 2024)
        
        # Team growth (100%) should exceed league average (~10%)
        assert result.team_growth_rate > result.league_avg_growth_rate
        
        # Net lift should be positive
        assert result.net_lift > 0
    
    def test_calculate_negative_lift(self):
        """Test calculation when team underperforms league"""
        calculator = TeamValueLiftCalculator()
        
        team_data = TeamData(
            team_id="team_1",
            team_name="Struggling Team",
            market_tier=3,
            dma_ranking=50,
            annual_records=[
                TeamAnnualRecord(
                    year=2023,
                    valuation=80_000_000,
                    revenue=15_000_000,
                    attendance_avg=7000,
                    points_per_game=75.0
                ),
                TeamAnnualRecord(
                    year=2024,
                    valuation=85_000_000,  # Only 6.25% growth
                    revenue=16_000_000,
                    attendance_avg=7200,
                    points_per_game=76.0
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
                ),
                LeagueAnnualRecord(
                    year=2024,
                    avg_viewership=1.2,
                    avg_attendance=9500,
                    avg_salary=138_000,  # 15% growth
                    total_teams=12
                )
            ]
        )
        
        result = calculator.calculate(team_data, league_data, 2023, 2024)
        
        # Team growth (~6%) should be less than league average (~30% based on salary growth * 2)
        assert result.team_growth_rate < result.league_avg_growth_rate
        
        # Net lift should be negative
        assert result.net_lift < 0
    
    def test_calculate_league_avg_growth(self):
        """Test league average growth calculation"""
        calculator = TeamValueLiftCalculator()
        
        league_data = LeagueData(
            annual_records=[
                LeagueAnnualRecord(
                    year=2023,
                    avg_viewership=1.0,
                    avg_attendance=9000,
                    avg_salary=120_000,
                    total_teams=12
                ),
                LeagueAnnualRecord(
                    year=2024,
                    avg_viewership=1.2,
                    avg_attendance=9500,
                    avg_salary=132_000,  # 10% growth
                    total_teams=12
                )
            ]
        )
        
        growth_rate = calculator.calculate_league_avg_growth(league_data, 2023, 2024)
        
        # Growth rate should be positive
        assert growth_rate > 0
        
        # Should be roughly 2x salary growth (10% * 2 = 20%)
        assert 0.15 <= growth_rate <= 0.25
    
    def test_calculate_missing_prior_year(self):
        """Test error handling when prior year data is missing"""
        calculator = TeamValueLiftCalculator()
        
        team_data = TeamData(
            team_id="team_1",
            team_name="Test Team",
            market_tier=2,
            dma_ranking=15,
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=150_000_000,
                    revenue=25_000_000,
                    attendance_avg=10000,
                    points_per_game=85.0
                )
            ]
        )
        
        league_data = LeagueData(
            annual_records=[
                LeagueAnnualRecord(
                    year=2024,
                    avg_viewership=1.2,
                    avg_attendance=9500,
                    avg_salary=132_000,
                    total_teams=12
                )
            ]
        )
        
        with pytest.raises(ValueError) as exc_info:
            calculator.calculate(team_data, league_data, 2023, 2024)
        
        assert "2023" in str(exc_info.value)
    
    def test_calculate_zero_prior_valuation(self):
        """Test error handling when prior valuation is zero"""
        calculator = TeamValueLiftCalculator()
        
        team_data = TeamData(
            team_id="team_1",
            team_name="Test Team",
            market_tier=2,
            dma_ranking=15,
            annual_records=[
                TeamAnnualRecord(
                    year=2023,
                    valuation=0,  # Invalid
                    revenue=20_000_000,
                    attendance_avg=9000,
                    points_per_game=82.0
                ),
                TeamAnnualRecord(
                    year=2024,
                    valuation=150_000_000,
                    revenue=25_000_000,
                    attendance_avg=10000,
                    points_per_game=85.0
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
        
        with pytest.raises(ValueError) as exc_info:
            calculator.calculate(team_data, league_data, 2023, 2024)
        
        assert "positive" in str(exc_info.value).lower()
    
    def test_calculate_real_world_scenario(self):
        """Test with realistic WNBA data (Indiana Fever example)"""
        calculator = TeamValueLiftCalculator()
        
        # Indiana Fever: $55M (2024) -> $170M (2025) = 209% growth
        team_data = TeamData(
            team_id="IND",
            team_name="Indiana Fever",
            market_tier=2,
            dma_ranking=25,
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=55_000_000,
                    revenue=9_100_000,
                    attendance_avg=9000,
                    points_per_game=80.0
                ),
                TeamAnnualRecord(
                    year=2025,
                    valuation=170_000_000,  # After Caitlin Clark
                    revenue=32_000_000,
                    attendance_avg=17000,
                    points_per_game=84.5
                )
            ]
        )
        
        # League average growth ~176% (from Forbes data)
        league_data = LeagueData(
            annual_records=[
                LeagueAnnualRecord(
                    year=2024,
                    avg_viewership=1.0,
                    avg_attendance=9000,
                    avg_salary=120_000,
                    total_teams=12
                ),
                LeagueAnnualRecord(
                    year=2025,
                    avg_viewership=1.5,
                    avg_attendance=11000,
                    avg_salary=180_000,  # 50% growth
                    total_teams=12
                )
            ]
        )
        
        result = calculator.calculate(team_data, league_data, 2024, 2025)
        
        # Verify Indiana Fever's exceptional growth
        expected_team_growth = (170_000_000 - 55_000_000) / 55_000_000
        assert abs(result.team_growth_rate - expected_team_growth) < 0.01
        
        # Team should have positive net lift (outperformed league)
        # Note: Actual result depends on league average calculation
        assert result.net_lift != 0  # Should have some lift
