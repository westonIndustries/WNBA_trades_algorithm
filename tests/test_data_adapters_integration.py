"""Integration tests for data adapters (WEHOOP and Statista)"""
import pytest
from unittest.mock import Mock, patch

from src.data_loaders import WEHOOPAdapter, StatistaAdapter
from src.models import PlayerData, TeamData


class TestWEHOOPAdapterIntegration:
    """Integration tests for WEHOOPAdapter"""
    
    def test_wehoop_adapter_initialization(self):
        """Test WEHOOP adapter can be initialized"""
        adapter = WEHOOPAdapter()
        assert adapter.max_retries == 3
        
        # Test custom retry count
        adapter_custom = WEHOOPAdapter(max_retries=5)
        assert adapter_custom.max_retries == 5
    
    def test_fetch_player_stats_without_rpy2(self):
        """Test fetch_player_stats raises error when rpy2 is not available"""
        adapter = WEHOOPAdapter()
        
        # Force rpy2 to be unavailable
        adapter._rpy2_available = False
        
        with pytest.raises(RuntimeError) as exc_info:
            adapter.fetch_player_stats("player_123", 2020, 2024)
        
        assert "rpy2 package not available" in str(exc_info.value)
    
    def test_fetch_team_stats_without_rpy2(self):
        """Test fetch_team_stats raises error when rpy2 is not available"""
        adapter = WEHOOPAdapter()
        
        # Force rpy2 to be unavailable
        adapter._rpy2_available = False
        
        with pytest.raises(RuntimeError) as exc_info:
            adapter.fetch_team_stats("team_456", 2020, 2024)
        
        assert "rpy2 package not available" in str(exc_info.value)
    
    @patch('src.data_loaders.wehoop_adapter.time.sleep')
    def test_fetch_player_stats_with_mock_wehoop(self, mock_sleep):
        """Test fetch_player_stats with mocked wehoop package"""
        adapter = WEHOOPAdapter()
        
        # Mock rpy2 availability
        adapter._rpy2_available = True
        
        # Mock the importr function
        mock_wehoop = Mock()
        adapter._importr = Mock(return_value=mock_wehoop)
        
        # Fetch player stats
        result = adapter.fetch_player_stats("player_123", 2020, 2022)
        
        # Verify result structure
        assert isinstance(result, PlayerData)
        assert result.player_id == "player_123"
        assert len(result.annual_records) == 3  # 2020, 2021, 2022
        
        # Verify annual records
        for i, record in enumerate(result.annual_records):
            expected_year = 2020 + i
            assert record.year == expected_year
            assert record.points_per_game > 0
            assert record.games_played > 0
    
    @patch('src.data_loaders.wehoop_adapter.time.sleep')
    def test_fetch_team_stats_with_mock_wehoop(self, mock_sleep):
        """Test fetch_team_stats with mocked wehoop package"""
        adapter = WEHOOPAdapter()
        
        # Mock rpy2 availability
        adapter._rpy2_available = True
        
        # Mock the importr function
        mock_wehoop = Mock()
        adapter._importr = Mock(return_value=mock_wehoop)
        
        # Fetch team stats
        result = adapter.fetch_team_stats("team_456", 2020, 2023)
        
        # Verify result structure
        assert isinstance(result, TeamData)
        assert result.team_id == "team_456"
        assert len(result.annual_records) == 4  # 2020, 2021, 2022, 2023
        
        # Verify annual records
        for i, record in enumerate(result.annual_records):
            expected_year = 2020 + i
            assert record.year == expected_year
            assert record.valuation > 0
            assert record.revenue > 0
            assert record.attendance_avg > 0
    
    @patch('src.data_loaders.wehoop_adapter.time.sleep')
    def test_fetch_player_stats_retry_logic(self, mock_sleep):
        """Test retry logic with exponential backoff"""
        adapter = WEHOOPAdapter(max_retries=3)
        adapter._rpy2_available = True
        
        # Mock importr to raise exception on first two calls, succeed on third
        call_count = [0]
        
        def mock_importr_side_effect(package_name):
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception("API temporarily unavailable")
            return Mock()
        
        adapter._importr = Mock(side_effect=mock_importr_side_effect)
        
        # Should succeed after retries
        result = adapter.fetch_player_stats("player_123", 2020, 2020)
        
        # Verify retries occurred
        assert call_count[0] == 3
        assert mock_sleep.call_count == 2  # Called twice (before 2nd and 3rd attempts)
        
        # Verify exponential backoff
        assert mock_sleep.call_args_list[0][0][0] == 1  # 2^0 = 1
        assert mock_sleep.call_args_list[1][0][0] == 2  # 2^1 = 2
    
    @patch('src.data_loaders.wehoop_adapter.time.sleep')
    def test_fetch_player_stats_max_retries_exceeded(self, mock_sleep):
        """Test that error is raised after max retries"""
        adapter = WEHOOPAdapter(max_retries=3)
        adapter._rpy2_available = True
        
        # Mock importr to always raise exception
        adapter._importr = Mock(side_effect=Exception("API unavailable"))
        
        # Should raise ValueError after max retries
        with pytest.raises(ValueError) as exc_info:
            adapter.fetch_player_stats("player_123", 2020, 2020)
        
        assert "Failed to fetch player stats after 3 attempts" in str(exc_info.value)
        assert mock_sleep.call_count == 2  # Called twice (before 2nd and 3rd attempts)


class TestStatistaAdapterIntegration:
    """Integration tests for StatistaAdapter"""
    
    def test_statista_adapter_initialization(self):
        """Test Statista adapter can be initialized"""
        adapter = StatistaAdapter()
        assert adapter._viewership_data == {}
        assert adapter._attendance_data == {}
        assert adapter._salary_data == {}
    
    def test_viewership_data_manual_entry(self):
        """Test manual entry and retrieval of viewership data"""
        adapter = StatistaAdapter()
        
        # Set viewership data
        adapter.set_viewership_data(2024, 1.2)
        adapter.set_viewership_data(2023, 1.0)
        
        # Retrieve viewership data
        assert adapter.get_viewership_data(2024) == 1.2
        assert adapter.get_viewership_data(2023) == 1.0
    
    def test_viewership_data_not_available(self):
        """Test error when viewership data is not available"""
        adapter = StatistaAdapter()
        
        with pytest.raises(ValueError) as exc_info:
            adapter.get_viewership_data(2024)
        
        assert "Viewership data for year 2024 not available" in str(exc_info.value)
        assert "manually enter data" in str(exc_info.value)
    
    def test_viewership_data_validation(self):
        """Test validation of viewership data"""
        adapter = StatistaAdapter()
        
        # Negative viewership should raise error
        with pytest.raises(ValueError) as exc_info:
            adapter.set_viewership_data(2024, -1.0)
        
        assert "Viewership must be non-negative" in str(exc_info.value)
    
    def test_attendance_data_manual_entry(self):
        """Test manual entry and retrieval of attendance data"""
        adapter = StatistaAdapter()
        
        # Set attendance data for multiple teams
        adapter.set_attendance_data("IND", 2024, 17000.0)
        adapter.set_attendance_data("LV", 2024, 9500.0)
        adapter.set_attendance_data("IND", 2023, 9000.0)
        
        # Retrieve attendance data
        assert adapter.get_attendance_data("IND", 2024) == 17000.0
        assert adapter.get_attendance_data("LV", 2024) == 9500.0
        assert adapter.get_attendance_data("IND", 2023) == 9000.0
    
    def test_attendance_data_not_available(self):
        """Test error when attendance data is not available"""
        adapter = StatistaAdapter()
        
        with pytest.raises(ValueError) as exc_info:
            adapter.get_attendance_data("IND", 2024)
        
        assert "Attendance data for team IND in year 2024 not available" in str(exc_info.value)
        assert "manually enter data" in str(exc_info.value)
    
    def test_attendance_data_validation(self):
        """Test validation of attendance data"""
        adapter = StatistaAdapter()
        
        # Negative attendance should raise error
        with pytest.raises(ValueError) as exc_info:
            adapter.set_attendance_data("IND", 2024, -100.0)
        
        assert "Attendance must be non-negative" in str(exc_info.value)
    
    def test_salary_data_manual_entry(self):
        """Test manual entry and retrieval of salary data"""
        adapter = StatistaAdapter()
        
        # Set salary data for multiple players
        adapter.set_salary_data("clark_c", 2024, 76000.0)
        adapter.set_salary_data("wilson_a", 2024, 200000.0)
        adapter.set_salary_data("clark_c", 2023, 0.0)  # Rookie year
        
        # Retrieve salary data
        assert adapter.get_salary_data("clark_c", 2024) == 76000.0
        assert adapter.get_salary_data("wilson_a", 2024) == 200000.0
        assert adapter.get_salary_data("clark_c", 2023) == 0.0
    
    def test_salary_data_not_available(self):
        """Test error when salary data is not available"""
        adapter = StatistaAdapter()
        
        with pytest.raises(ValueError) as exc_info:
            adapter.get_salary_data("clark_c", 2024)
        
        assert "Salary data for player clark_c in year 2024 not available" in str(exc_info.value)
        assert "manually enter data" in str(exc_info.value)
    
    def test_salary_data_validation(self):
        """Test validation of salary data"""
        adapter = StatistaAdapter()
        
        # Negative salary should raise error
        with pytest.raises(ValueError) as exc_info:
            adapter.set_salary_data("clark_c", 2024, -1000.0)
        
        assert "Salary must be non-negative" in str(exc_info.value)
    
    def test_statista_adapter_multiple_years(self):
        """Test Statista adapter with multiple years of data"""
        adapter = StatistaAdapter()
        
        # Set up multi-year data
        years = [2020, 2021, 2022, 2023, 2024]
        for year in years:
            adapter.set_viewership_data(year, 0.5 + (year - 2020) * 0.1)
            adapter.set_attendance_data("IND", year, 8000.0 + (year - 2020) * 500)
            adapter.set_salary_data("player_1", year, 50000.0 + (year - 2020) * 10000)
        
        # Verify all data is retrievable
        for year in years:
            viewership = adapter.get_viewership_data(year)
            attendance = adapter.get_attendance_data("IND", year)
            salary = adapter.get_salary_data("player_1", year)
            
            assert viewership > 0
            assert attendance > 0
            assert salary > 0
    
    def test_statista_adapter_real_world_scenario(self):
        """Test Statista adapter with realistic WNBA data"""
        adapter = StatistaAdapter()
        
        # Simulate Caitlin Clark impact on Indiana Fever
        # Before Clark (2023)
        adapter.set_attendance_data("IND", 2023, 9000.0)
        adapter.set_viewership_data(2023, 0.5)
        
        # After Clark (2024)
        adapter.set_attendance_data("IND", 2024, 17000.0)
        adapter.set_viewership_data(2024, 1.2)
        adapter.set_salary_data("clark_c", 2024, 76000.0)
        
        # Verify the data
        assert adapter.get_attendance_data("IND", 2024) > adapter.get_attendance_data("IND", 2023)
        assert adapter.get_viewership_data(2024) > adapter.get_viewership_data(2023)
        assert adapter.get_salary_data("clark_c", 2024) == 76000.0
        
        # Calculate attendance increase
        attendance_increase = (
            adapter.get_attendance_data("IND", 2024) - 
            adapter.get_attendance_data("IND", 2023)
        )
        assert attendance_increase == 8000.0  # 89% increase
