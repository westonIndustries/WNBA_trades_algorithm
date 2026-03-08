"""CSV data loader for Forbes valuations and market tiers"""
import csv
from typing import List, Dict
from pathlib import Path

from src.models import TeamAnnualRecord, MarketTierData


class CSVLoader:
    """Load data from CSV files"""
    
    def load_forbes_valuations(self, filepath: str, year: int = 2025) -> List[TeamAnnualRecord]:
        """
        Load Forbes team valuation data from CSV
        
        Args:
            filepath: Path to Forbes CSV file
            year: Year of the data (default: 2025)
            
        Returns:
            List of TeamAnnualRecord objects
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV is malformed or missing required columns
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                # Read with tab delimiter (based on file structure)
                reader = csv.DictReader(f, delimiter='\t')
                
                records = []
                for row in reader:
                    # Validate required columns
                    if not all(key in row for key in ['Team', 'Valuation', 'Revenue']):
                        raise ValueError(f"Missing required columns in CSV: {filepath}")
                    
                    # Parse valuation and revenue (remove $ and M, convert to float)
                    valuation_str = row['Valuation'].replace('$', '').replace('M', '').strip()
                    revenue_str = row['Revenue'].replace('$', '').replace('M', '').strip()
                    
                    try:
                        valuation = float(valuation_str) * 1_000_000  # Convert M to actual value
                        revenue = float(revenue_str) * 1_000_000
                    except ValueError as e:
                        raise ValueError(f"Invalid numeric value in CSV: {e}")
                    
                    record = TeamAnnualRecord(
                        year=year,
                        valuation=valuation,
                        revenue=revenue,
                        attendance_avg=0.0,  # Not in Forbes data
                        points_per_game=0.0  # Not in Forbes data
                    )
                    records.append(record)
                
                if not records:
                    raise ValueError(f"No data found in CSV: {filepath}")
                
                return records
                
        except csv.Error as e:
            raise ValueError(f"Malformed CSV file: {e}")
    
    def load_market_tiers(self, filepath: str) -> Dict[str, MarketTierData]:
        """
        Load market tier classifications from CSV
        
        Args:
            filepath: Path to market tier CSV file
            
        Returns:
            Dictionary mapping tier name to MarketTierData
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV is malformed or missing required columns
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Group teams by tier
                tiers: Dict[int, List[str]] = {1: [], 2: [], 3: []}
                tier_factors = {1: 1.25, 2: 1.0, 3: 0.85}
                
                for row in reader:
                    if not all(key in row for key in ['Team', 'Tier']):
                        raise ValueError(f"Missing required columns in CSV: {filepath}")
                    
                    team = row['Team'].strip()
                    try:
                        tier = int(row['Tier'])
                        if tier not in [1, 2, 3]:
                            raise ValueError(f"Invalid tier value: {tier}. Must be 1, 2, or 3")
                    except ValueError as e:
                        raise ValueError(f"Invalid tier value in CSV: {e}")
                    
                    tiers[tier].append(team)
                
                # Create MarketTierData objects
                result = {}
                for tier_num, teams in tiers.items():
                    if teams:  # Only create if tier has teams
                        result[f"Tier {tier_num}"] = MarketTierData(
                            tier=tier_num,
                            adjustment_factor=tier_factors[tier_num],
                            teams=teams
                        )
                
                if not result:
                    raise ValueError(f"No valid tier data found in CSV: {filepath}")
                
                return result
                
        except csv.Error as e:
            raise ValueError(f"Malformed CSV file: {e}")
