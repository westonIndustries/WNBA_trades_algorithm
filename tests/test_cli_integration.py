"""Integration tests for CLI interface"""
import pytest
import json
import sys
from io import StringIO
from unittest.mock import patch
from pathlib import Path

from src.cli import main, create_parser, load_data, create_player_data, create_team_data, create_league_data


class TestCLIIntegration:
    """Integration tests for command-line interface"""
    
    def test_cli_help_displays_correctly(self):
        """Test that CLI help message displays without errors"""
        parser = create_parser()
        
        # Capture help output
        with patch('sys.stdout', new=StringIO()) as fake_out:
            try:
                parser.parse_args(['--help'])
            except SystemExit:
                pass  # argparse exits after showing help
            
            help_text = fake_out.getvalue()
            
            # Verify key elements are in help text
            assert 'brand-portability' in help_text
            assert '--player-id' in help_text
            assert '--new-team-id' in help_text
            assert '--json' in help_text
    
    def test_load_data_with_valid_files(self):
        """Test loading data from valid CSV and JSON files"""
        # Create mock args
        class Args:
            forbes_data = 'data/Forbes top 12 most valueable wnba teams 2025.csv'
            market_tiers_2024 = 'data/WNBA 2024 market tiers data.json'
            market_tiers_2026 = 'data/WNBA 2026 Market Tiers.json'
            current_year = 2025
        
        args = Args()
        
        # Load data
        forbes_data, market_tiers_2024, market_tiers_2026 = load_data(args)
        
        # Verify data was loaded
        assert len(forbes_data) > 0
        assert 'tiers' in market_tiers_2024
        assert 'tiers' in market_tiers_2026
        assert len(market_tiers_2024['tiers']) > 0
        assert len(market_tiers_2026['tiers']) > 0
    
    def test_load_data_with_missing_file(self):
        """Test error handling when data file is missing"""
        class Args:
            forbes_data = 'data/nonexistent_file.csv'
            market_tiers_2024 = 'data/WNBA 2024 market tiers data.json'
            market_tiers_2026 = 'data/WNBA 2026 Market Tiers.json'
            current_year = 2025
        
        args = Args()
        
        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            load_data(args)
    
    def test_create_player_data_with_valid_args(self):
        """Test creating PlayerData from command-line arguments"""
        class Args:
            player_id = 'clark_caitlin'
            player_name = 'Caitlin Clark'
            player_ppg = 19.2
            player_salary = 76000.0
            player_games = 40
            player_minutes = 35.0
            new_team_id = 'indiana_fever'
            current_year = 2025
        
        args = Args()
        
        player_data = create_player_data(args)
        
        assert player_data.player_id == 'clark_caitlin'
        assert player_data.player_name == 'Caitlin Clark'
        assert len(player_data.annual_records) == 1
        assert player_data.annual_records[0].points_per_game == 19.2
        assert player_data.annual_records[0].salary == 76000.0
    
    def test_create_player_data_with_missing_fields(self):
        """Test error handling when required player data is missing"""
        class Args:
            player_id = 'clark_caitlin'
            player_name = 'Caitlin Clark'
            player_ppg = None  # Missing
            player_salary = 76000.0
            player_games = 40
            player_minutes = 35.0
            new_team_id = 'indiana_fever'
            current_year = 2025
        
        args = Args()
        
        with pytest.raises(ValueError, match="Missing required player data"):
            create_player_data(args)
    
    def test_create_team_data_with_valid_args(self):
        """Test creating TeamData from loaded data"""
        # Load real data
        class LoadArgs:
            forbes_data = 'data/Forbes top 12 most valueable wnba teams 2025.csv'
            market_tiers_2024 = 'data/WNBA 2024 market tiers data.json'
            market_tiers_2026 = 'data/WNBA 2026 Market Tiers.json'
            current_year = 2025
        
        load_args = LoadArgs()
        forbes_data, market_tiers_2024, market_tiers_2026 = load_data(load_args)
        
        # Create team data
        class Args:
            new_team_id = 'indiana_fever'
            team_ppg = 84.5
            prior_year = 2024
            current_year = 2025
        
        args = Args()
        
        team_data = create_team_data(args, forbes_data, market_tiers_2024, market_tiers_2026)
        
        assert team_data.team_id == 'indiana_fever'
        assert team_data.market_tier in [1, 2, 3]
        assert team_data.dma_ranking > 0
        assert len(team_data.annual_records) >= 1
    
    def test_create_team_data_with_invalid_team(self):
        """Test error handling when team is not found"""
        # Load real data
        class LoadArgs:
            forbes_data = 'data/Forbes top 12 most valueable wnba teams 2025.csv'
            market_tiers_2024 = 'data/WNBA 2024 market tiers data.json'
            market_tiers_2026 = 'data/WNBA 2026 Market Tiers.json'
            current_year = 2025
        
        load_args = LoadArgs()
        forbes_data, market_tiers_2024, market_tiers_2026 = load_data(load_args)
        
        class Args:
            new_team_id = 'nonexistent_team'
            team_ppg = 84.5
            prior_year = 2024
            current_year = 2025
        
        args = Args()
        
        with pytest.raises(ValueError, match="not found in market tier data"):
            create_team_data(args, forbes_data, market_tiers_2024, market_tiers_2026)
    
    def test_create_league_data(self):
        """Test creating LeagueData from loaded data"""
        # Load real data
        class Args:
            forbes_data = 'data/Forbes top 12 most valueable wnba teams 2025.csv'
            market_tiers_2024 = 'data/WNBA 2024 market tiers data.json'
            market_tiers_2026 = 'data/WNBA 2026 Market Tiers.json'
            current_year = 2025
        
        args = Args()
        forbes_data, market_tiers_2024, _ = load_data(args)
        
        league_data = create_league_data(forbes_data, market_tiers_2024)
        
        assert len(league_data.annual_records) > 0
        assert league_data.annual_records[0].total_teams == 12
        assert league_data.annual_records[0].avg_viewership > 0
    
    @patch('sys.argv', [
        'brand-portability',
        '--player-id', 'clark_caitlin',
        '--new-team-id', 'indiana_fever',
        '--player-name', 'Caitlin Clark',
        '--player-ppg', '19.2',
        '--player-salary', '76000',
        '--player-games', '40',
        '--player-minutes', '35.0',
        '--team-ppg', '84.5',
        '--json'
    ])
    def test_end_to_end_calculation_json_output(self):
        """Test end-to-end calculation with JSON output"""
        # Capture stdout
        with patch('sys.stdout', new=StringIO()) as fake_out:
            exit_code = main()
            
            # Verify successful execution
            assert exit_code == 0
            
            # Verify JSON output
            output = fake_out.getvalue()
            result = json.loads(output)
            
            # Verify structure
            assert 'brandPortability' in result
            assert 'components' in result
            assert 'formula' in result
            assert 'interpretation' in result
            assert 'warnings' in result
            
            # Verify components
            assert 'careerBaseline' in result['components']
            assert 'marketAdjustment' in result['components']
            assert 'revenueDelta' in result['components']
            assert 'teamValueLift' in result['components']
    
    @patch('sys.argv', [
        'brand-portability',
        '--player-id', 'clark_caitlin',
        '--new-team-id', 'indiana_fever',
        '--player-name', 'Caitlin Clark',
        '--player-ppg', '19.2',
        '--player-salary', '76000',
        '--player-games', '40',
        '--player-minutes', '35.0',
        '--team-ppg', '84.5'
    ])
    def test_end_to_end_calculation_text_output(self):
        """Test end-to-end calculation with readable text output"""
        # Capture stdout
        with patch('sys.stdout', new=StringIO()) as fake_out:
            exit_code = main()
            
            # Verify successful execution
            assert exit_code == 0
            
            # Verify text output
            output = fake_out.getvalue()
            
            # Verify key sections are present
            assert 'BRAND PORTABILITY ANALYSIS' in output
            assert 'Brand Portability Score' in output
            assert 'INTERPRETATION:' in output
            assert 'COMPONENT BREAKDOWN' in output
            assert 'Career Historical Baseline' in output
            assert 'Market Adjustment Factor' in output
            assert 'Revenue Delta' in output
            assert 'Team Value Lift' in output
    
    @patch('sys.argv', [
        'brand-portability',
        '--player-id', 'clark_caitlin',
        '--new-team-id', 'indiana_fever',
        '--player-name', 'Caitlin Clark',
        '--player-ppg', '19.2',
        '--player-salary', '76000',
        '--player-games', '40',
        '--player-minutes', '35.0',
        '--team-ppg', '84.5',
        '--forbes-data', 'data/nonexistent.csv'
    ])
    def test_error_handling_missing_file(self):
        """Test error handling when data file is missing"""
        # Capture stderr
        with patch('sys.stderr', new=StringIO()) as fake_err:
            exit_code = main()
            
            # Verify error exit code
            assert exit_code == 1
            
            # Verify error message
            error_output = fake_err.getvalue()
            assert 'Error: Data file not found' in error_output
    
    @patch('sys.argv', [
        'brand-portability',
        '--player-id', 'clark_caitlin',
        '--new-team-id', 'indiana_fever',
        '--player-name', 'Caitlin Clark',
        '--player-ppg', '19.2',
        '--player-salary', '76000',
        '--player-games', '40',
        # Missing --player-minutes
        '--team-ppg', '84.5'
    ])
    def test_error_handling_missing_required_data(self):
        """Test error handling when required player data is missing"""
        # Capture stderr
        with patch('sys.stderr', new=StringIO()) as fake_err:
            exit_code = main()
            
            # Verify error exit code
            assert exit_code == 1
            
            # Verify error message
            error_output = fake_err.getvalue()
            assert 'Error: Invalid data' in error_output
            assert 'Missing required player data' in error_output
    
    @patch('sys.argv', [
        'brand-portability',
        '--player-id', 'clark_caitlin',
        '--new-team-id', 'nonexistent_team',
        '--player-name', 'Caitlin Clark',
        '--player-ppg', '19.2',
        '--player-salary', '76000',
        '--player-games', '40',
        '--player-minutes', '35.0',
        '--team-ppg', '84.5'
    ])
    def test_error_handling_invalid_team(self):
        """Test error handling when team is not found"""
        # Capture stderr
        with patch('sys.stderr', new=StringIO()) as fake_err:
            exit_code = main()
            
            # Verify error exit code
            assert exit_code == 1
            
            # Verify error message
            error_output = fake_err.getvalue()
            assert 'Error: Invalid data' in error_output
            assert 'not found in market tier data' in error_output
    
    @patch('sys.argv', [
        'brand-portability',
        '--player-id', 'clark_caitlin',
        '--new-team-id', 'indiana_fever',
        '--player-name', 'Caitlin Clark',
        '--player-ppg', '19.2',
        '--player-salary', '76000',
        '--player-games', '40',
        '--player-minutes', '35.0',
        '--team-ppg', '84.5',
        '--verbose'
    ])
    def test_verbose_mode_includes_traceback(self):
        """Test that verbose mode includes detailed error information"""
        # This test verifies verbose mode works, but doesn't trigger an error
        # Just verify it runs successfully with verbose flag
        with patch('sys.stdout', new=StringIO()):
            exit_code = main()
            assert exit_code == 0
    
    def test_output_format_json_vs_text(self):
        """Test that JSON and text outputs contain same data"""
        base_args = [
            'brand-portability',
            '--player-id', 'clark_caitlin',
            '--new-team-id', 'indiana_fever',
            '--player-name', 'Caitlin Clark',
            '--player-ppg', '19.2',
            '--player-salary', '76000',
            '--player-games', '40',
            '--player-minutes', '35.0',
            '--team-ppg', '84.5'
        ]
        
        # Get JSON output
        with patch('sys.argv', base_args + ['--json']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                json_output = fake_out.getvalue()
                json_result = json.loads(json_output)
        
        # Get text output
        with patch('sys.argv', base_args):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                text_output = fake_out.getvalue()
        
        # Verify chi value appears in both
        chi_value = json_result['brandPortability']
        assert f"{chi_value:.2f}" in text_output
        
        # Verify interpretation appears in both
        interpretation = json_result['interpretation']
        assert interpretation in text_output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
