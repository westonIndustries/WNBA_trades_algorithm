#!/usr/bin/env python3
"""Command-line interface for Brand Portability Formula calculator"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from src.models import PlayerData, PlayerAnnualRecord, TeamData, TeamAnnualRecord, LeagueData, LeagueAnnualRecord, MarketTierData
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


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser for CLI
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='brand-portability',
        description='Calculate Brand Portability Formula (χ) for WNBA players',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calculate portability with JSON output
  python -m src.cli --player-id "clark_caitlin" --new-team-id "indiana_fever" --json
  
  # Calculate portability with readable text output
  python -m src.cli --player-id "clark_caitlin" --new-team-id "indiana_fever"
  
  # Specify custom data file paths
  python -m src.cli --player-id "clark_caitlin" --new-team-id "indiana_fever" \\
    --forbes-data data/custom_forbes.csv \\
    --market-tiers-2024 data/custom_2024.json
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--player-id',
        required=True,
        help='Player identifier (e.g., "clark_caitlin")'
    )
    
    parser.add_argument(
        '--new-team-id',
        required=True,
        help='New team identifier (e.g., "indiana_fever")'
    )
    
    # Optional data file paths
    parser.add_argument(
        '--forbes-data',
        default='data/Forbes top 12 most valueable wnba teams 2025.csv',
        help='Path to Forbes valuation CSV file (default: data/Forbes top 12 most valueable wnba teams 2025.csv)'
    )
    
    parser.add_argument(
        '--market-tiers-2024',
        default='data/WNBA 2024 market tiers data.json',
        help='Path to 2024 market tiers JSON file (default: data/WNBA 2024 market tiers data.json)'
    )
    
    parser.add_argument(
        '--market-tiers-2026',
        default='data/WNBA 2026 Market Tiers.json',
        help='Path to 2026 market tiers JSON file (default: data/WNBA 2026 Market Tiers.json)'
    )
    
    # Player data arguments
    parser.add_argument(
        '--player-name',
        help='Player full name (e.g., "Caitlin Clark")'
    )
    
    parser.add_argument(
        '--player-ppg',
        type=float,
        help='Player points per game'
    )
    
    parser.add_argument(
        '--player-salary',
        type=float,
        help='Player annual salary'
    )
    
    parser.add_argument(
        '--player-games',
        type=int,
        help='Games played by player'
    )
    
    parser.add_argument(
        '--player-minutes',
        type=float,
        help='Player average minutes per game'
    )
    
    # Team data arguments
    parser.add_argument(
        '--team-ppg',
        type=float,
        help='Team points per game'
    )
    
    parser.add_argument(
        '--prior-year',
        type=int,
        default=2024,
        help='Prior year for team value lift calculation (default: 2024)'
    )
    
    parser.add_argument(
        '--current-year',
        type=int,
        default=2025,
        help='Current year for team value lift calculation (default: 2025)'
    )
    
    # Output format
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON (default: human-readable text)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose error messages'
    )
    
    return parser


def load_data(args: argparse.Namespace) -> tuple:
    """
    Load all required data from files
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Tuple of (forbes_data, market_tiers_2024, market_tiers_2026)
        
    Raises:
        FileNotFoundError: If required data files are missing
        ValueError: If data files are malformed
    """
    csv_loader = CSVLoader()
    json_loader = JSONLoader()
    
    # Load Forbes valuations
    forbes_data = csv_loader.load_forbes_valuations(args.forbes_data, year=args.current_year)
    
    # Load market tiers
    market_tiers_2024 = json_loader.load_market_tiers_2024(args.market_tiers_2024)
    market_tiers_2026 = json_loader.load_market_tiers_2026(args.market_tiers_2026)
    
    return forbes_data, market_tiers_2024, market_tiers_2026


def create_player_data(args: argparse.Namespace) -> PlayerData:
    """
    Create PlayerData from command-line arguments
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        PlayerData instance
        
    Raises:
        ValueError: If required player data is missing
    """
    # Validate required player data
    required_fields = ['player_name', 'player_ppg', 'player_salary', 'player_games', 'player_minutes']
    missing_fields = [field for field in required_fields if getattr(args, field) is None]
    
    if missing_fields:
        raise ValueError(
            f"Missing required player data: {', '.join(f'--{field.replace('_', '-')}' for field in missing_fields)}"
        )
    
    # Create player annual record (simplified - single year for MVP)
    annual_record = PlayerAnnualRecord(
        year=args.current_year,
        team_id=args.new_team_id,
        points_per_game=args.player_ppg,
        games_played=args.player_games,
        minutes_per_game=args.player_minutes,
        salary=args.player_salary,
        scoring_percentile=None  # Will be calculated by estimators
    )
    
    return PlayerData(
        player_id=args.player_id,
        player_name=args.player_name,
        annual_records=[annual_record]
    )


def create_team_data(args: argparse.Namespace, forbes_data: list, market_tiers_2024: dict, market_tiers_2026: dict) -> TeamData:
    """
    Create TeamData for new team from loaded data
    
    Args:
        args: Parsed command-line arguments
        forbes_data: List of TeamAnnualRecord from Forbes (2025 data)
        market_tiers_2024: Market tier data from 2024 JSON
        market_tiers_2026: Market tier data from 2026 JSON
        
    Returns:
        TeamData instance
        
    Raises:
        ValueError: If team not found in data or required data is missing
    """
    # Find team in market tiers to get tier and DMA ranking
    team_tier = None
    team_dma = None
    
    for tier_name, tier_data in market_tiers_2026['tiers'].items():
        if args.new_team_id in [team.lower().replace(' ', '_') for team in tier_data.teams]:
            team_tier = tier_data.tier
            # Find exact team name match
            for team_name in tier_data.teams:
                if team_name.lower().replace(' ', '_') == args.new_team_id:
                    team_dma = market_tiers_2026['team_dma_rankings'].get(team_name, 50)
                    break
            break
    
    if team_tier is None:
        raise ValueError(f"Team '{args.new_team_id}' not found in market tier data")
    
    # Validate required team data
    if args.team_ppg is None:
        raise ValueError("Missing required team data: --team-ppg")
    
    # Create team annual records from both 2024 and 2025 data
    annual_records = []
    
    # Add 2024 data from market_tiers_2024
    for team_name, record_2024 in market_tiers_2024.get('team_records_2024', []):
        if team_name.lower().replace(' ', '_') == args.new_team_id:
            record_2024.points_per_game = args.team_ppg
            annual_records.append(record_2024)
            break
    
    # Add 2025 data from Forbes
    if forbes_data:
        record_2025 = forbes_data[0]  # Use first record as template
        record_2025.year = args.current_year
        record_2025.points_per_game = args.team_ppg
        annual_records.append(record_2025)
    
    # If no 2024 data found, create a synthetic record
    if not any(r.year == args.prior_year for r in annual_records):
        # Create synthetic 2024 record based on 2025 data
        if forbes_data:
            record_2024 = TeamAnnualRecord(
                year=args.prior_year,
                valuation=forbes_data[0].valuation * 0.5,  # Approximate 2024 valuation
                revenue=forbes_data[0].revenue * 0.5,  # Approximate 2024 revenue
                attendance_avg=0.0,
                points_per_game=args.team_ppg
            )
            annual_records.insert(0, record_2024)
    
    return TeamData(
        team_id=args.new_team_id,
        team_name=args.new_team_id.replace('_', ' ').title(),
        market_tier=team_tier,
        dma_ranking=team_dma,
        annual_records=annual_records
    )


def create_league_data(forbes_data: list, market_tiers_2024: dict) -> LeagueData:
    """
    Create LeagueData from loaded data
    
    Args:
        forbes_data: List of TeamAnnualRecord from Forbes
        market_tiers_2024: Market tier data from 2024 JSON
        
    Returns:
        LeagueData instance
    """
    # Calculate league averages from Forbes data
    if forbes_data:
        avg_valuation = sum(record.valuation for record in forbes_data) / len(forbes_data)
        avg_revenue = sum(record.revenue for record in forbes_data) / len(forbes_data)
    else:
        avg_valuation = 0.0
        avg_revenue = 0.0
    
    # Create league annual record
    league_record = LeagueAnnualRecord(
        year=2025,
        avg_viewership=1_500_000,  # Approximate from Statista data
        avg_attendance=8_500,  # Approximate from Statista data
        avg_salary=120_000,  # Approximate from Statista data
        total_teams=12
    )
    
    return LeagueData(annual_records=[league_record])


def calculate_portability(
    player_data: PlayerData,
    team_data: TeamData,
    league_data: LeagueData,
    market_tier_data: MarketTierData,
    args: argparse.Namespace
) -> 'BrandPortabilityResult':
    """
    Calculate brand portability using all calculators
    
    Args:
        player_data: Player career data
        team_data: New team data
        league_data: League-wide data
        market_tier_data: Market tier classification
        args: Command-line arguments
        
    Returns:
        BrandPortabilityResult
    """
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
    
    career_baseline_calc = CareerBaselineCalculator(
        revenue_attributor=player_revenue_attributor
    )
    
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
        team_data_history=[team_data],  # Simplified - using current team
        prior_year=args.prior_year,
        current_year=args.current_year,
        player_contribution_weight=0.35
    )
    
    return result


def main() -> int:
    """
    Main CLI entry point
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Load data from files
        forbes_data, market_tiers_2024, market_tiers_2026 = load_data(args)
        
        # Create data models
        player_data = create_player_data(args)
        team_data = create_team_data(args, forbes_data, market_tiers_2024, market_tiers_2026)
        league_data = create_league_data(forbes_data, market_tiers_2024)
        
        # Get market tier data for new team
        market_tier_data = None
        for tier_name, tier_data in market_tiers_2026['tiers'].items():
            if tier_data.tier == team_data.market_tier:
                market_tier_data = tier_data
                break
        
        if market_tier_data is None:
            raise ValueError(f"Market tier data not found for tier {team_data.market_tier}")
        
        # Calculate brand portability
        result = calculate_portability(
            player_data=player_data,
            team_data=team_data,
            league_data=league_data,
            market_tier_data=market_tier_data,
            args=args
        )
        
        # Format and output results
        formatter = ResultFormatter()
        
        if args.json:
            output = formatter.to_json(result)
        else:
            output = formatter.to_readable_text(result)
        
        print(output)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: Data file not found - {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
        
    except ValueError as e:
        print(f"Error: Invalid data - {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
        
    except Exception as e:
        print(f"Error: Unexpected error occurred - {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
