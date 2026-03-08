#!/usr/bin/env python3
"""
Example usage of Brand Portability Formula calculator

This script demonstrates how to calculate brand portability for a WNBA player
using the Maya Vance from Indiana Fever to Golden State Valkyries scenario as an example.
"""

from src.models import (
    PlayerData, PlayerAnnualRecord,
    TeamData, TeamAnnualRecord,
    LeagueData, LeagueAnnualRecord,
    MarketTierData
)
from src.data_loaders.csv_loader import CSVLoader
from src.data_loaders.json_loader import JSONLoader
from src.estimators.merchandise_estimator import MerchandiseEstimator
from src.estimators.tv_rating_estimator import TVRatingEstimator
from src.estimators.ticket_premium_estimator import TicketPremiumEstimator
from src.estimators.player_revenue_attributor import PlayerRevenueAttributor
from src.calculators.revenue_delta_calculator import RevenueDeltaCalculator
from src.calculators.team_value_lift_calculator import TeamValueLiftCalculator
from src.calculators.career_baseline_calculator import CareerBaselineCalculator
from src.calculators.market_adjustment_calculator import MarketAdjustmentCalculator
from src.calculators.brand_portability_calculator import BrandPortabilityCalculator
from src.formatters.result_formatter import ResultFormatter


def load_data_from_files():
    """
    Load data from local CSV and JSON files
    
    Returns:
        Tuple of (forbes_data, market_tiers_2024, market_tiers_2026)
    """
    print("Loading data from files...")
    
    csv_loader = CSVLoader()
    json_loader = JSONLoader()
    
    # Load Forbes 2025 valuations
    forbes_data = csv_loader.load_forbes_valuations(
        'data/Forbes top 12 most valueable wnba teams 2025.csv',
        year=2025
    )
    
    # Load market tier data
    market_tiers_2024 = json_loader.load_market_tiers_2024(
        'data/WNBA 2024 market tiers data.json'
    )
    market_tiers_2026 = json_loader.load_market_tiers_2026(
        'data/WNBA 2026 Market Tiers.json'
    )
    
    print(f"✓ Loaded {len(forbes_data)} team records from Forbes data")
    print(f"✓ Loaded market tier data for 2024 and 2026")
    
    return forbes_data, market_tiers_2024, market_tiers_2026


def create_maya_vance_data():
    """
    Create PlayerData for Maya Vance
    
    Based on her 2025 season with Indiana Fever:
    - 8.5 PPG (points per game)
    - 35 games played
    - 22.0 minutes per game
    - $85,000 salary
    
    Returns:
        PlayerData instance
    """
    print("\nCreating player data for Maya Vance...")
    
    # Create annual record for 2025 season
    annual_record = PlayerAnnualRecord(
        year=2025,
        team_id="indiana_fever",
        points_per_game=8.5,
        games_played=35,
        minutes_per_game=22.0,
        salary=85000.0,
        scoring_percentile=0.65  # Mid-tier scorer in WNBA
    )
    
    player_data = PlayerData(
        player_id="vance_maya",
        player_name="Maya Vance",
        annual_records=[annual_record]
    )
    
    print(f"✓ Created player data: {player_data.player_name}")
    print(f"  - {annual_record.points_per_game} PPG")
    print(f"  - {annual_record.games_played} games played")
    print(f"  - ${annual_record.salary:,.0f} salary")
    
    return player_data


def create_golden_state_data(forbes_data, market_tiers_2024, market_tiers_2026):
    """
    Create TeamData for Golden State Valkyries
    
    Args:
        forbes_data: List of TeamAnnualRecord from Forbes
        market_tiers_2024: 2024 market tier data
        market_tiers_2026: 2026 market tier data
        
    Returns:
        TeamData instance
    """
    print("\nCreating team data for Golden State Valkyries...")
    
    # Golden State Valkyries (Tier 1 market - San Francisco Bay Area)
    valkyries_tier = 1
    valkyries_dma = 6  # San Francisco-Oakland-San Jose DMA ranking
    
    # Create annual records for 2025 and 2026 (expansion team)
    annual_records = [
        TeamAnnualRecord(
            year=2025,
            valuation=85_000_000,  # 2025 expansion valuation (estimated)
            revenue=12_000_000,  # 2025 revenue (expansion baseline)
            attendance_avg=7_500,  # Initial attendance
            points_per_game=82.3
        ),
        TeamAnnualRecord(
            year=2026,
            valuation=120_000_000,  # 2026 valuation (estimated with growth)
            revenue=18_000_000,  # 2026 revenue (estimated with Maya Vance)
            attendance_avg=9_500,  # Post-trade attendance
            points_per_game=82.3
        )
    ]
    
    team_data = TeamData(
        team_id="golden_state_valkyries",
        team_name="Golden State Valkyries",
        market_tier=valkyries_tier,
        dma_ranking=valkyries_dma,
        annual_records=annual_records
    )
    
    print(f"✓ Created team data: {team_data.team_name}")
    print(f"  - Market Tier: {team_data.market_tier} (Large market)")
    print(f"  - DMA Ranking: {team_data.dma_ranking}")
    print(f"  - 2025 Valuation: ${annual_records[0].valuation:,.0f}")
    print(f"  - 2026 Valuation: ${annual_records[1].valuation:,.0f} (+41%)")
    
    return team_data


def create_league_data():
    """
    Create LeagueData with WNBA league-wide statistics
    
    Returns:
        LeagueData instance
    """
    print("\nCreating league data...")
    
    league_record = LeagueAnnualRecord(
        year=2026,
        avg_viewership=1_500_000,  # Average viewership from Statista
        avg_attendance=8_500,  # Average attendance from Statista
        avg_salary=120_000,  # Average salary from Statista
        total_teams=13  # 13 teams with Golden State expansion
    )
    
    league_data = LeagueData(annual_records=[league_record])
    
    print(f"✓ Created league data for {league_record.year}")
    print(f"  - {league_record.total_teams} teams")
    print(f"  - Avg viewership: {league_record.avg_viewership:,}")
    
    return league_data


def get_market_tier_data(market_tiers_2026, tier: int):
    """
    Get MarketTierData for a specific tier
    
    Args:
        market_tiers_2026: Market tier data from JSON
        tier: Tier number (1, 2, or 3)
        
    Returns:
        MarketTierData instance
    """
    for tier_name, tier_data in market_tiers_2026['tiers'].items():
        if tier_data.tier == tier:
            return tier_data
    
    raise ValueError(f"Market tier {tier} not found")


def calculate_brand_portability(player_data, team_data, league_data, market_tier_data):
    """
    Calculate brand portability score
    
    Args:
        player_data: Player career data
        team_data: New team data
        league_data: League-wide data
        market_tier_data: Market tier classification
        
    Returns:
        BrandPortabilityResult
    """
    print("\n" + "="*60)
    print("CALCULATING BRAND PORTABILITY")
    print("="*60)
    
    # Initialize estimators
    merchandise_estimator = MerchandiseEstimator()
    tv_rating_estimator = TVRatingEstimator()
    ticket_premium_estimator = TicketPremiumEstimator()
    player_revenue_attributor = PlayerRevenueAttributor()
    
    # Initialize calculators
    revenue_delta_calc = RevenueDeltaCalculator(
        merchandise_estimator=merchandise_estimator,
        tv_rating_estimator=tv_rating_estimator,
        ticket_premium_estimator=ticket_premium_estimator
    )
    
    team_value_lift_calc = TeamValueLiftCalculator()
    career_baseline_calc = CareerBaselineCalculator(revenue_attributor=player_revenue_attributor)
    market_adjustment_calc = MarketAdjustmentCalculator()
    
    # Initialize main calculator
    calculator = BrandPortabilityCalculator(
        revenue_delta_calc=revenue_delta_calc,
        team_value_lift_calc=team_value_lift_calc,
        career_baseline_calc=career_baseline_calc,
        market_adjustment_calc=market_adjustment_calc
    )
    
    # Calculate portability
    result = calculator.calculate_portability(
        player_data=player_data,
        new_team_data=team_data,
        league_data=league_data,
        market_tier_data=market_tier_data,
        team_data_history=[team_data],
        prior_year=2025,
        current_year=2026,
        player_contribution_weight=0.30
    )
    
    return result


def display_results(result):
    """
    Display calculation results in human-readable format
    
    Args:
        result: BrandPortabilityResult
    """
    formatter = ResultFormatter()
    
    # Display readable text output
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(formatter.to_readable_text(result))
    
    # Also save JSON output to file
    json_output = formatter.to_json(result)
    with open('example_output.json', 'w') as f:
        f.write(json_output)
    
    print("\n✓ JSON output saved to: example_output.json")


def main():
    """
    Main example execution
    
    This demonstrates the complete workflow:
    1. Load data from files
    2. Create player, team, and league data models
    3. Calculate brand portability
    4. Display and interpret results
    """
    print("="*60)
    print("BRAND PORTABILITY FORMULA - EXAMPLE")
    print("Scenario: Maya Vance from Indiana Fever to Golden State")
    print("="*60)
    
    try:
        # Step 1: Load data from files
        forbes_data, market_tiers_2024, market_tiers_2026 = load_data_from_files()
        
        # Step 2: Create data models
        player_data = create_maya_vance_data()
        team_data = create_golden_state_data(forbes_data, market_tiers_2024, market_tiers_2026)
        league_data = create_league_data()
        market_tier_data = get_market_tier_data(market_tiers_2026, team_data.market_tier)
        
        # Step 3: Calculate brand portability
        result = calculate_brand_portability(
            player_data=player_data,
            team_data=team_data,
            league_data=league_data,
            market_tier_data=market_tier_data
        )
        
        # Step 4: Display results
        display_results(result)
        
        print("\n" + "="*60)
        print("EXAMPLE COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
