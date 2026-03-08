"""JSON data loader for market tiers"""
import json
from typing import Dict, Any
from pathlib import Path

from src.models import MarketTierData, TeamAnnualRecord


class JSONLoader:
    """Load data from JSON files"""
    
    def load_market_tiers_2024(self, filepath: str) -> Dict[str, Any]:
        """
        Load 2024 market tiers data from JSON
        
        Args:
            filepath: Path to 2024 market tiers JSON file
            
        Returns:
            Dictionary containing market tier data with team valuations and revenue
            
        Raises:
            FileNotFoundError: If JSON file doesn't exist
            ValueError: If JSON is malformed or missing required structure
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {filepath}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            if "WNBA_Market_Data_2024" not in data:
                raise ValueError("Missing 'WNBA_Market_Data_2024' key in JSON")
            
            market_data = data["WNBA_Market_Data_2024"]
            
            # Parse tiers and extract team data
            result = {
                "tiers": {},
                "team_records_2024": [],
                "team_records_2023": []
            }
            
            for tier_name, tier_data in market_data.items():
                if "Adjustment_Factor" not in tier_data or "Teams" not in tier_data:
                    raise ValueError(f"Missing required fields in tier: {tier_name}")
                
                # Extract tier number from name (e.g., "Tier 1 (High Efficiency)" -> 1)
                tier_num = 1 if "Tier 1" in tier_name else (2 if "Tier 2" in tier_name else 3)
                
                teams = []
                for team in tier_data["Teams"]:
                    if "name" not in team:
                        raise ValueError(f"Missing 'name' field in team data")
                    
                    teams.append(team["name"])
                    
                    # Create TeamAnnualRecord for 2024 valuation
                    if "valuation_2024" in team:
                        record_2024 = TeamAnnualRecord(
                            year=2024,
                            valuation=float(team["valuation_2024"]) * 1_000_000,  # Convert M to actual
                            revenue=0.0,  # Revenue is from 2023
                            attendance_avg=0.0,
                            points_per_game=0.0
                        )
                        result["team_records_2024"].append((team["name"], record_2024))
                    
                    # Create TeamAnnualRecord for 2023 revenue
                    if "rev_2023" in team:
                        record_2023 = TeamAnnualRecord(
                            year=2023,
                            valuation=0.0,  # Valuation is from 2024
                            revenue=float(team["rev_2023"]) * 1_000_000,
                            attendance_avg=0.0,
                            points_per_game=0.0
                        )
                        result["team_records_2023"].append((team["name"], record_2023))
                
                result["tiers"][tier_name] = MarketTierData(
                    tier=tier_num,
                    adjustment_factor=float(tier_data["Adjustment_Factor"]),
                    teams=teams
                )
            
            if not result["tiers"]:
                raise ValueError("No valid tier data found in JSON")
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Malformed JSON file: {e}")
    
    def load_market_tiers_2026(self, filepath: str) -> Dict[str, Any]:
        """
        Load 2026 market tiers projections from JSON
        
        Args:
            filepath: Path to 2026 market tiers JSON file
            
        Returns:
            Dictionary containing market tier data with DMA rankings and valuation estimates
            
        Raises:
            FileNotFoundError: If JSON file doesn't exist
            ValueError: If JSON is malformed or missing required structure
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {filepath}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            if "WNBA_Market_Data" not in data:
                raise ValueError("Missing 'WNBA_Market_Data' key in JSON")
            
            market_data = data["WNBA_Market_Data"]
            
            # Parse tiers
            result = {
                "tiers": {},
                "team_dma_rankings": {},
                "team_valuations_2026": []
            }
            
            for tier_name, tier_data in market_data.items():
                if "Adjustment_Factor" not in tier_data or "Teams" not in tier_data:
                    raise ValueError(f"Missing required fields in tier: {tier_name}")
                
                # Extract tier number from name (e.g., "Tier 1" -> 1)
                tier_num = int(tier_name.split()[-1])
                
                teams = []
                for team in tier_data["Teams"]:
                    if "name" not in team:
                        raise ValueError(f"Missing 'name' field in team data")
                    
                    team_name = team["name"]
                    teams.append(team_name)
                    
                    # Store DMA ranking
                    if "dma_rank" in team:
                        result["team_dma_rankings"][team_name] = team["dma_rank"]
                    
                    # Create TeamAnnualRecord for 2026 valuation estimate
                    if "valuation_est" in team:
                        record_2026 = TeamAnnualRecord(
                            year=2026,
                            valuation=float(team["valuation_est"]) * 1_000_000,
                            revenue=0.0,
                            attendance_avg=0.0,
                            points_per_game=0.0
                        )
                        result["team_valuations_2026"].append((team_name, record_2026))
                
                result["tiers"][tier_name] = MarketTierData(
                    tier=tier_num,
                    adjustment_factor=float(tier_data["Adjustment_Factor"]),
                    teams=teams
                )
            
            if not result["tiers"]:
                raise ValueError("No valid tier data found in JSON")
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Malformed JSON file: {e}")
