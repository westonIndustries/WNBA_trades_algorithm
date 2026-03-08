"""Property-based tests for CSVLoader

Feature: brand-portability-formula
Property: CSV parsing preserves data integrity
Validates: Data Requirements - Data Format
"""
import pytest
import tempfile
import csv
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume

from src.data_loaders import CSVLoader
from src.models import TeamAnnualRecord, MarketTierData


# Strategy for generating valid team names (ASCII only for CSV compatibility)
team_names = st.text(
    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ',
    min_size=3,
    max_size=30
).filter(lambda x: x.strip() and not x.startswith(' ') and not x.endswith(' '))

# Strategy for generating valid valuations (in millions)
valuations = st.floats(min_value=50.0, max_value=1000.0, allow_nan=False, allow_infinity=False)

# Strategy for generating valid revenues (in millions)
revenues = st.floats(min_value=5.0, max_value=100.0, allow_nan=False, allow_infinity=False)

# Strategy for generating valid years
years = st.integers(min_value=2020, max_value=2030)

# Strategy for generating valid tiers
tiers = st.integers(min_value=1, max_value=3)


class TestCSVLoaderProperty:
    """Property-based tests for CSVLoader"""
    
    @given(
        team_data=st.lists(
            st.tuples(team_names, valuations, revenues),
            min_size=1,
            max_size=15,
            unique_by=lambda x: x[0]  # Unique team names
        ),
        year=years
    )
    @settings(max_examples=100, deadline=None)
    def test_forbes_csv_parsing_preserves_data_integrity(self, team_data, year):
        """
        Property: CSV parsing preserves data integrity
        
        For any valid set of team data (names, valuations, revenues),
        when written to CSV and read back, the data should be preserved
        with correct conversions (millions to actual values).
        """
        loader = CSVLoader()
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            
            # Write header
            writer.writerow(['Team', 'Valuation', 'Revenue'])
            
            # Write data (format with 1 decimal place, which will cause rounding)
            for team_name, valuation, revenue in team_data:
                # Round to 1 decimal place to match what will be written
                valuation_rounded = round(valuation, 1)
                revenue_rounded = round(revenue, 1)
                writer.writerow([team_name, f'${valuation_rounded:.1f}M', f'${revenue_rounded:.1f}M'])
            
            temp_path = f.name
        
        try:
            # Load the CSV
            records = loader.load_forbes_valuations(temp_path, year)
            
            # Verify data integrity
            assert len(records) == len(team_data), "Number of records should match input"
            
            for i, (team_name, valuation, revenue) in enumerate(team_data):
                record = records[i]
                
                # Verify year is preserved
                assert record.year == year
                
                # Verify valuation is preserved (with rounding to 1 decimal place)
                # The CSV format uses .1f which rounds, so we need to account for that
                valuation_rounded = round(valuation, 1)
                expected_valuation = valuation_rounded * 1_000_000
                assert abs(record.valuation - expected_valuation) < 1.0, \
                    f"Valuation mismatch: expected {expected_valuation}, got {record.valuation}"
                
                # Verify revenue is preserved (with rounding to 1 decimal place)
                revenue_rounded = round(revenue, 1)
                expected_revenue = revenue_rounded * 1_000_000
                assert abs(record.revenue - expected_revenue) < 1.0, \
                    f"Revenue mismatch: expected {expected_revenue}, got {record.revenue}"
                
                # Verify other fields are initialized
                assert record.attendance_avg == 0.0
                assert record.points_per_game == 0.0
        
        finally:
            # Clean up
            Path(temp_path).unlink()
    
    @given(
        tier_data=st.lists(
            st.tuples(team_names, tiers),
            min_size=1,
            max_size=15,
            unique_by=lambda x: x[0]  # Unique team names
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_market_tier_csv_parsing_preserves_data_integrity(self, tier_data):
        """
        Property: CSV parsing preserves data integrity for market tiers
        
        For any valid set of team tier assignments,
        when written to CSV and read back, the tier assignments
        should be preserved with correct grouping.
        """
        loader = CSVLoader()
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Team', 'Tier'])
            
            # Write data
            for team_name, tier in tier_data:
                writer.writerow([team_name, tier])
            
            temp_path = f.name
        
        try:
            # Load the CSV
            result = loader.load_market_tiers(temp_path)
            
            # Verify data integrity
            # Count teams by tier in input
            input_tier_counts = {1: 0, 2: 0, 3: 0}
            for team_name, tier in tier_data:
                input_tier_counts[tier] += 1
            
            # Count teams by tier in output
            output_tier_counts = {1: 0, 2: 0, 3: 0}
            for tier_name, tier_obj in result.items():
                output_tier_counts[tier_obj.tier] += len(tier_obj.teams)
            
            # Verify counts match
            for tier_num in [1, 2, 3]:
                assert output_tier_counts[tier_num] == input_tier_counts[tier_num], \
                    f"Tier {tier_num} count mismatch: expected {input_tier_counts[tier_num]}, got {output_tier_counts[tier_num]}"
            
            # Verify all teams are present
            all_output_teams = []
            for tier_obj in result.values():
                all_output_teams.extend(tier_obj.teams)
            
            input_teams = [team_name for team_name, _ in tier_data]
            assert len(all_output_teams) == len(input_teams), "Total team count should match"
            
            # Verify adjustment factors are correct
            tier_factors = {1: 1.25, 2: 1.0, 3: 0.85}
            for tier_name, tier_obj in result.items():
                expected_factor = tier_factors[tier_obj.tier]
                assert tier_obj.adjustment_factor == expected_factor, \
                    f"Adjustment factor for tier {tier_obj.tier} should be {expected_factor}"
        
        finally:
            # Clean up
            Path(temp_path).unlink()
    
    @given(
        valuation=valuations,
        revenue=revenues,
        year=years
    )
    @settings(max_examples=100, deadline=None)
    def test_numeric_precision_preserved(self, valuation, revenue, year):
        """
        Property: Numeric precision is preserved during CSV parsing
        
        For any valid numeric values, the conversion from millions to actual values
        should preserve precision within acceptable floating-point error bounds.
        """
        loader = CSVLoader()
        
        # Create temporary CSV with single record
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['Team', 'Valuation', 'Revenue'])
            writer.writerow(['Test Team', f'${valuation:.2f}M', f'${revenue:.2f}M'])
            temp_path = f.name
        
        try:
            records = loader.load_forbes_valuations(temp_path, year)
            
            # Verify precision (allow for floating point rounding)
            expected_valuation = valuation * 1_000_000
            expected_revenue = revenue * 1_000_000
            
            # Allow 0.1% error for floating point precision and rounding
            valuation_error = abs(records[0].valuation - expected_valuation) / expected_valuation
            revenue_error = abs(records[0].revenue - expected_revenue) / expected_revenue
            
            assert valuation_error < 0.001, f"Valuation precision error too large: {valuation_error}"
            assert revenue_error < 0.001, f"Revenue precision error too large: {revenue_error}"
        
        finally:
            Path(temp_path).unlink()
    
    @given(
        team_count=st.integers(min_value=1, max_value=20),
        year=years
    )
    @settings(max_examples=100, deadline=None)
    def test_csv_row_count_preserved(self, team_count, year):
        """
        Property: Number of CSV rows equals number of parsed records
        
        For any valid number of teams, the number of records parsed
        should exactly match the number of data rows in the CSV.
        """
        loader = CSVLoader()
        
        # Create temporary CSV with specified number of teams
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['Team', 'Valuation', 'Revenue'])
            
            for i in range(team_count):
                writer.writerow([f'Team {i}', f'${100.0}M', f'${20.0}M'])
            
            temp_path = f.name
        
        try:
            records = loader.load_forbes_valuations(temp_path, year)
            
            # Verify row count matches
            assert len(records) == team_count, \
                f"Expected {team_count} records, got {len(records)}"
        
        finally:
            Path(temp_path).unlink()
    
    @given(
        team_name=team_names,
        valuation=valuations,
        revenue=revenues
    )
    @settings(max_examples=100, deadline=None)
    def test_csv_parsing_idempotent(self, team_name, valuation, revenue):
        """
        Property: CSV parsing is idempotent
        
        Parsing the same CSV file multiple times should produce identical results.
        """
        loader = CSVLoader()
        
        # Create temporary CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['Team', 'Valuation', 'Revenue'])
            writer.writerow([team_name, f'${valuation:.1f}M', f'${revenue:.1f}M'])
            temp_path = f.name
        
        try:
            # Parse twice
            records1 = loader.load_forbes_valuations(temp_path, 2024)
            records2 = loader.load_forbes_valuations(temp_path, 2024)
            
            # Verify identical results
            assert len(records1) == len(records2)
            assert records1[0].year == records2[0].year
            assert records1[0].valuation == records2[0].valuation
            assert records1[0].revenue == records2[0].revenue
        
        finally:
            Path(temp_path).unlink()
