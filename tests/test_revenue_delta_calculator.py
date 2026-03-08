"""Unit tests for RevenueDeltaCalculator"""
import pytest

from src.calculators import RevenueDeltaCalculator, RevenueDeltaResult
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


class TestRevenueDeltaCalculator:
    """Unit tests for RevenueDeltaCalculator"""
    
    def test_calculate_basic(self):
        """Test basic revenue delta calculation"""
        # Create estimators
        merch_est = MerchandiseEstimator()
        tv_est = TVRatingEstimator()
        ticket_est = TicketPremiumEstimator()
        
        calculator = RevenueDeltaCalculator(merch_est, tv_est, ticket_est)
        
        # Create player data
        player_data = PlayerData(
            player_id="player_1",
            player_name="Test Player",
            annual_records=[
                PlayerAnnualRecord(
                    year=2023,
                    team_id="team_old",
                    points_per_game=18.0,
                    games_played=40,
                    minutes_per_game=32.0,
                    salary=100_000,
                    scoring_percentile=0.75
                )
            ]
        )
        
        # Create new team data
        new_team_data = TeamData(
            team_id="team_new",
            team_name="New Team",
            market_tier=1,  # Tier 1 market
            dma_ranking=5,
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=200_000_000,
                    revenue=30_000_000,
                    attendance_avg=12000,
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
                )
            ]
        )
        
        # Calculate revenue delta
        result = calculator.calculate(player_data, new_team_data, league_data)
        
        # Verify result structure
        assert isinstance(result, RevenueDeltaResult)
        assert isinstance(result.total_delta, float)
        assert isinstance(result.career_avg_revenue, float)
        assert isinstance(result.new_city_revenue, float)
        assert isinstance(result.components, dict)
        
        # Verify components exist
        assert "merchandise" in result.components
        assert "tv_rating" in result.components
        assert "ticket_premium" in result.components
        
        # Verify delta calculation
        expected_delta = result.new_city_revenue - result.career_avg_revenue
        assert abs(result.total_delta - expected_delta) < 0.01
    
    def test_calculate_component_breakdown(self):
        """Test that component breakdown is accurate"""
        merch_est = MerchandiseEstimator()
        tv_est = TVRatingEstimator()
        ticket_est = TicketPremiumEstimator()
        
        calculator = RevenueDeltaCalculator(merch_est, tv_est, ticket_est)
        
        player_data = PlayerData(
            player_id="player_1",
            player_name="Test Player",
            annual_records=[
                PlayerAnnualRecord(
                    year=2023,
                    team_id="team_old",
                    points_per_game=20.0,
                    games_played=40,
                    minutes_per_game=35.0,
                    salary=150_000,
                    scoring_percentile=0.85
                )
            ]
        )
        
        new_team_data = TeamData(
            team_id="team_new",
            team_name="New Team",
            market_tier=2,
            dma_ranking=15,
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=150_000_000,
                    revenue=25_000_000,
                    attendance_avg=10000,
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
        
        result = calculator.calculate(player_data, new_team_data, league_data)
        
        # Verify components sum to total delta
        component_sum = sum(result.components.values())
        assert abs(result.total_delta - component_sum) < 0.01
    
    def test_calculate_tier_1_market(self):
        """Test calculation for Tier 1 (large) market"""
        merch_est = MerchandiseEstimator()
        tv_est = TVRatingEstimator()
        ticket_est = TicketPremiumEstimator()
        
        calculator = RevenueDeltaCalculator(merch_est, tv_est, ticket_est)
        
        player_data = PlayerData(
            player_id="player_1",
            player_name="Star Player",
            annual_records=[
                PlayerAnnualRecord(
                    year=2023,
                    team_id="team_old",
                    points_per_game=22.0,
                    games_played=40,
                    minutes_per_game=36.0,
                    salary=200_000,
                    scoring_percentile=0.95
                )
            ]
        )
        
        new_team_data = TeamData(
            team_id="team_new",
            team_name="Big Market Team",
            market_tier=1,  # Tier 1 market
            dma_ranking=1,  # Top market
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=400_000_000,
                    revenue=50_000_000,
                    attendance_avg=15000,
                    points_per_game=88.0
                )
            ]
        )
        
        league_data = LeagueData(
            annual_records=[
                LeagueAnnualRecord(
                    year=2023,
                    avg_viewership=1.2,
                    avg_attendance=10000,
                    avg_salary=130_000,
                    total_teams=12
                )
            ]
        )
        
        result = calculator.calculate(player_data, new_team_data, league_data)
        
        # Tier 1 market should generally have positive revenue delta
        # (assuming player moves to larger market)
        assert result.new_city_revenue > 0
        assert result.career_avg_revenue > 0
    
    def test_calculate_no_player_data(self):
        """Test error handling when player has no career data"""
        merch_est = MerchandiseEstimator()
        tv_est = TVRatingEstimator()
        ticket_est = TicketPremiumEstimator()
        
        calculator = RevenueDeltaCalculator(merch_est, tv_est, ticket_est)
        
        player_data = PlayerData(
            player_id="player_1",
            player_name="Rookie",
            annual_records=[]  # No career data
        )
        
        new_team_data = TeamData(
            team_id="team_new",
            team_name="New Team",
            market_tier=2,
            dma_ranking=20,
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=150_000_000,
                    revenue=25_000_000,
                    attendance_avg=10000,
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
        
        with pytest.raises(ValueError) as exc_info:
            calculator.calculate(player_data, new_team_data, league_data)
        
        assert "career data" in str(exc_info.value).lower()
    
    def test_calculate_multi_year_career(self):
        """Test calculation with multi-year career data"""
        merch_est = MerchandiseEstimator()
        tv_est = TVRatingEstimator()
        ticket_est = TicketPremiumEstimator()
        
        calculator = RevenueDeltaCalculator(merch_est, tv_est, ticket_est)
        
        player_data = PlayerData(
            player_id="player_1",
            player_name="Veteran Player",
            annual_records=[
                PlayerAnnualRecord(
                    year=2021,
                    team_id="team_old",
                    points_per_game=16.0,
                    games_played=38,
                    minutes_per_game=30.0,
                    salary=80_000,
                    scoring_percentile=0.65
                ),
                PlayerAnnualRecord(
                    year=2022,
                    team_id="team_old",
                    points_per_game=18.0,
                    games_played=40,
                    minutes_per_game=32.0,
                    salary=100_000,
                    scoring_percentile=0.75
                ),
                PlayerAnnualRecord(
                    year=2023,
                    team_id="team_old",
                    points_per_game=20.0,
                    games_played=40,
                    minutes_per_game=34.0,
                    salary=120_000,
                    scoring_percentile=0.85
                )
            ]
        )
        
        new_team_data = TeamData(
            team_id="team_new",
            team_name="New Team",
            market_tier=1,
            dma_ranking=8,
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=250_000_000,
                    revenue=35_000_000,
                    attendance_avg=13000,
                    points_per_game=86.0
                )
            ]
        )
        
        league_data = LeagueData(
            annual_records=[
                LeagueAnnualRecord(
                    year=2021,
                    avg_viewership=0.8,
                    avg_attendance=8500,
                    avg_salary=110_000,
                    total_teams=12
                ),
                LeagueAnnualRecord(
                    year=2022,
                    avg_viewership=0.9,
                    avg_attendance=9000,
                    avg_salary=115_000,
                    total_teams=12
                ),
                LeagueAnnualRecord(
                    year=2023,
                    avg_viewership=1.0,
                    avg_attendance=9500,
                    avg_salary=120_000,
                    total_teams=12
                )
            ]
        )
        
        result = calculator.calculate(player_data, new_team_data, league_data)
        
        # Career average should be computed across all years
        assert result.career_avg_revenue > 0
        assert result.new_city_revenue > 0
        
        # Verify result structure
        assert len(result.components) == 3
