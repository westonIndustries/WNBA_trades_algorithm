"""Unit tests for Career Baseline Calculator"""
import pytest

from src.calculators import CareerBaselineCalculator, CareerBaselineResult
from src.estimators import PlayerRevenueAttributor
from src.models import PlayerData, PlayerAnnualRecord, TeamData, TeamAnnualRecord


class TestCareerBaselineCalculator:
    """Unit tests for CareerBaselineCalculator"""
    
    def test_calculate_with_known_career_data(self):
        """Test career baseline calculation with known career data"""
        # Create player with 3 years of career data
        player_records = [
            PlayerAnnualRecord(
                year=2022,
                team_id="IND",
                points_per_game=19.2,
                games_played=40,
                minutes_per_game=35.0,
                salary=76_000
            ),
            PlayerAnnualRecord(
                year=2023,
                team_id="IND",
                points_per_game=20.5,
                games_played=38,
                minutes_per_game=36.0,
                salary=85_000
            ),
            PlayerAnnualRecord(
                year=2024,
                team_id="IND",
                points_per_game=22.1,
                games_played=40,
                minutes_per_game=37.0,
                salary=95_000
            )
        ]
        
        player_data = PlayerData(
            player_id="P1",
            player_name="Test Player",
            annual_records=player_records
        )
        
        # Create team data with revenue growth
        team_records = [
            # 2022 data
            TeamAnnualRecord(year=2022, valuation=100_000_000, revenue=15_000_000, 
                           attendance_avg=10000, points_per_game=84.5),
            TeamAnnualRecord(year=2021, valuation=95_000_000, revenue=10_000_000,
                           attendance_avg=9000, points_per_game=82.0),
            # 2023 data
            TeamAnnualRecord(year=2023, valuation=150_000_000, revenue=20_000_000,
                           attendance_avg=12000, points_per_game=86.0),
            # 2024 data
            TeamAnnualRecord(year=2024, valuation=200_000_000, revenue=25_000_000,
                           attendance_avg=14000, points_per_game=88.0),
        ]
        
        team_data = TeamData(
            team_id="IND",
            team_name="Indiana Fever",
            market_tier=2,
            dma_ranking=25,
            annual_records=team_records
        )
        
        # Create calculator
        revenue_attributor = PlayerRevenueAttributor()
        calculator = CareerBaselineCalculator(revenue_attributor)
        
        # Calculate career baseline
        result = calculator.calculate(player_data, [team_data])
        
        # Verify result structure
        assert isinstance(result, CareerBaselineResult)
        assert result.avg_annual_output > 0
        assert result.total_years == 3
        assert len(result.annual_breakdown) == 3
        
        # Verify years are correct
        years = [year for year, _ in result.annual_breakdown]
        assert years == [2022, 2023, 2024]
        
        # Verify all annual outputs are non-negative
        for year, output in result.annual_breakdown:
            assert output >= 0, f"Output for year {year} should be non-negative"
        
        # Verify average calculation
        total_output = sum(output for _, output in result.annual_breakdown)
        expected_avg = total_output / 3
        assert abs(result.avg_annual_output - expected_avg) < 0.01
    
    def test_calculate_with_single_year(self):
        """Test career baseline calculation with single year of data"""
        player_records = [
            PlayerAnnualRecord(
                year=2024,
                team_id="IND",
                points_per_game=20.0,
                games_played=40,
                minutes_per_game=35.0,
                salary=80_000
            )
        ]
        
        player_data = PlayerData(
            player_id="P1",
            player_name="Test Player",
            annual_records=player_records
        )
        
        team_records = [
            TeamAnnualRecord(year=2024, valuation=150_000_000, revenue=20_000_000,
                           attendance_avg=12000, points_per_game=85.0),
            TeamAnnualRecord(year=2023, valuation=140_000_000, revenue=15_000_000,
                           attendance_avg=11000, points_per_game=83.0),
        ]
        
        team_data = TeamData(
            team_id="IND",
            team_name="Indiana Fever",
            market_tier=2,
            dma_ranking=25,
            annual_records=team_records
        )
        
        revenue_attributor = PlayerRevenueAttributor()
        calculator = CareerBaselineCalculator(revenue_attributor)
        
        result = calculator.calculate(player_data, [team_data])
        
        # Should work with single year
        assert result.total_years == 1
        assert len(result.annual_breakdown) == 1
        assert result.avg_annual_output > 0
        
        # Average should equal the single year output
        single_year_output = result.annual_breakdown[0][1]
        assert abs(result.avg_annual_output - single_year_output) < 0.01
    
    def test_calculate_with_multiple_years(self):
        """Test career baseline calculation with multiple years of data"""
        # Create player with 5 years of career data
        player_records = []
        for i in range(5):
            year = 2020 + i
            player_records.append(
                PlayerAnnualRecord(
                    year=year,
                    team_id="IND",
                    points_per_game=15.0 + i,
                    games_played=40,
                    minutes_per_game=30.0,
                    salary=70_000 + (i * 5_000)
                )
            )
        
        player_data = PlayerData(
            player_id="P1",
            player_name="Test Player",
            annual_records=player_records
        )
        
        # Create team data
        team_records = []
        for i in range(5):
            year = 2020 + i
            team_records.append(
                TeamAnnualRecord(
                    year=year,
                    valuation=100_000_000 + (i * 10_000_000),
                    revenue=12_000_000 + (i * 2_000_000),
                    attendance_avg=10000 + (i * 500),
                    points_per_game=80.0
                )
            )
            # Add prior year data
            team_records.append(
                TeamAnnualRecord(
                    year=year - 1,
                    valuation=100_000_000 + ((i-1) * 10_000_000),
                    revenue=12_000_000 + ((i-1) * 2_000_000),
                    attendance_avg=10000 + ((i-1) * 500),
                    points_per_game=78.0
                )
            )
        
        team_data = TeamData(
            team_id="IND",
            team_name="Indiana Fever",
            market_tier=2,
            dma_ranking=25,
            annual_records=team_records
        )
        
        revenue_attributor = PlayerRevenueAttributor()
        calculator = CareerBaselineCalculator(revenue_attributor)
        
        result = calculator.calculate(player_data, [team_data])
        
        # Verify 5 years of data
        assert result.total_years == 5
        assert len(result.annual_breakdown) == 5
        assert result.avg_annual_output > 0
    
    def test_zero_career_baseline_raises_error(self):
        """Test that zero career baseline raises ValueError"""
        # Create player with zero performance
        player_records = [
            PlayerAnnualRecord(
                year=2024,
                team_id="IND",
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
        
        team_records = [
            TeamAnnualRecord(year=2024, valuation=150_000_000, revenue=20_000_000,
                           attendance_avg=12000, points_per_game=85.0),
            TeamAnnualRecord(year=2023, valuation=140_000_000, revenue=20_000_000,
                           attendance_avg=11000, points_per_game=83.0),
        ]
        
        team_data = TeamData(
            team_id="IND",
            team_name="Indiana Fever",
            market_tier=2,
            dma_ranking=25,
            annual_records=team_records
        )
        
        revenue_attributor = PlayerRevenueAttributor()
        calculator = CareerBaselineCalculator(revenue_attributor)
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="zero career baseline"):
            calculator.calculate(player_data, [team_data])
    
    def test_no_career_data_raises_error(self):
        """Test that player with no career data raises ValueError"""
        player_data = PlayerData(
            player_id="P1",
            player_name="Test Player",
            annual_records=[]
        )
        
        team_data = TeamData(
            team_id="IND",
            team_name="Indiana Fever",
            market_tier=2,
            dma_ranking=25,
            annual_records=[]
        )
        
        revenue_attributor = PlayerRevenueAttributor()
        calculator = CareerBaselineCalculator(revenue_attributor)
        
        with pytest.raises(ValueError, match="at least one year of career data"):
            calculator.calculate(player_data, [team_data])
    
    def test_no_team_data_raises_error(self):
        """Test that missing team data raises ValueError"""
        player_records = [
            PlayerAnnualRecord(
                year=2024,
                team_id="IND",
                points_per_game=20.0,
                games_played=40,
                minutes_per_game=35.0,
                salary=80_000
            )
        ]
        
        player_data = PlayerData(
            player_id="P1",
            player_name="Test Player",
            annual_records=player_records
        )
        
        revenue_attributor = PlayerRevenueAttributor()
        calculator = CareerBaselineCalculator(revenue_attributor)
        
        with pytest.raises(ValueError, match="Team data history must be provided"):
            calculator.calculate(player_data, [])
    
    def test_player_switches_teams(self):
        """Test career baseline when player switches teams"""
        # Player plays for two different teams
        player_records = [
            PlayerAnnualRecord(
                year=2022,
                team_id="TEAM1",
                points_per_game=18.0,
                games_played=40,
                minutes_per_game=32.0,
                salary=75_000
            ),
            PlayerAnnualRecord(
                year=2023,
                team_id="TEAM2",
                points_per_game=20.0,
                games_played=38,
                minutes_per_game=35.0,
                salary=85_000
            )
        ]
        
        player_data = PlayerData(
            player_id="P1",
            player_name="Test Player",
            annual_records=player_records
        )
        
        # Create data for both teams
        team1_records = [
            TeamAnnualRecord(year=2022, valuation=100_000_000, revenue=15_000_000,
                           attendance_avg=10000, points_per_game=82.0),
            TeamAnnualRecord(year=2021, valuation=95_000_000, revenue=12_000_000,
                           attendance_avg=9500, points_per_game=80.0),
        ]
        
        team2_records = [
            TeamAnnualRecord(year=2023, valuation=120_000_000, revenue=18_000_000,
                           attendance_avg=11000, points_per_game=85.0),
            TeamAnnualRecord(year=2022, valuation=115_000_000, revenue=16_000_000,
                           attendance_avg=10500, points_per_game=83.0),
        ]
        
        team1_data = TeamData(
            team_id="TEAM1",
            team_name="Team 1",
            market_tier=2,
            dma_ranking=30,
            annual_records=team1_records
        )
        
        team2_data = TeamData(
            team_id="TEAM2",
            team_name="Team 2",
            market_tier=1,
            dma_ranking=10,
            annual_records=team2_records
        )
        
        revenue_attributor = PlayerRevenueAttributor()
        calculator = CareerBaselineCalculator(revenue_attributor)
        
        # Should handle multiple teams
        result = calculator.calculate(player_data, [team1_data, team2_data])
        
        assert result.total_years == 2
        assert len(result.annual_breakdown) == 2
        assert result.avg_annual_output > 0
        
        # Verify both years are present
        years = [year for year, _ in result.annual_breakdown]
        assert 2022 in years
        assert 2023 in years
