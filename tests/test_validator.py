"""
Unit tests for Brand Portability Validator.

Tests correlation calculations, outlier detection, and consistency checks.
"""

import pytest
from src.validation.validator import (
    BrandPortabilityValidator,
    ValidationResult,
    OutlierResult
)


class TestAttendanceCorrelationAnalysis:
    """Tests for attendance_correlation_analysis method"""
    
    def test_perfect_positive_correlation(self):
        """Test with perfectly correlated data"""
        validator = BrandPortabilityValidator()
        
        estimated = [100.0, 200.0, 300.0, 400.0, 500.0]
        actual = [10.0, 20.0, 30.0, 40.0, 50.0]
        
        result = validator.attendance_correlation_analysis(estimated, actual)
        
        assert result.passed is True
        assert result.metric_value == pytest.approx(1.0, abs=0.01)
        assert result.threshold == 0.7
        assert "PASS" in result.message
        assert result.details["n_samples"] == 5
    
    def test_strong_positive_correlation(self):
        """Test with strong but not perfect correlation"""
        validator = BrandPortabilityValidator()
        
        estimated = [100.0, 200.0, 300.0, 400.0, 500.0]
        actual = [12.0, 19.0, 31.0, 38.0, 52.0]  # Slight noise
        
        result = validator.attendance_correlation_analysis(estimated, actual)
        
        assert result.passed is True
        assert result.metric_value > 0.7
        assert "PASS" in result.message
    
    def test_weak_correlation_fails(self):
        """Test with weak correlation that should fail"""
        validator = BrandPortabilityValidator()
        
        estimated = [100.0, 200.0, 300.0, 400.0, 500.0]
        actual = [50.0, 10.0, 40.0, 20.0, 30.0]  # Random order
        
        result = validator.attendance_correlation_analysis(estimated, actual)
        
        assert result.passed is False
        assert result.metric_value < 0.7
        assert "FAIL" in result.message
    
    def test_negative_correlation(self):
        """Test with negative correlation"""
        validator = BrandPortabilityValidator()
        
        estimated = [100.0, 200.0, 300.0, 400.0, 500.0]
        actual = [50.0, 40.0, 30.0, 20.0, 10.0]  # Inverse
        
        result = validator.attendance_correlation_analysis(estimated, actual)
        
        assert result.passed is False
        assert result.metric_value < 0
    
    def test_empty_lists_raises_error(self):
        """Test that empty lists raise ValueError"""
        validator = BrandPortabilityValidator()
        
        with pytest.raises(ValueError, match="cannot be empty"):
            validator.attendance_correlation_analysis([], [])
    
    def test_mismatched_lengths_raises_error(self):
        """Test that mismatched list lengths raise ValueError"""
        validator = BrandPortabilityValidator()
        
        with pytest.raises(ValueError, match="same length"):
            validator.attendance_correlation_analysis([1.0, 2.0], [1.0, 2.0, 3.0])


class TestValuationJumpAnalysis:
    """Tests for valuation_jump_analysis method"""
    
    def test_positive_correlation_passes(self):
        """Test that positive correlation between chi and valuation passes"""
        validator = BrandPortabilityValidator()
        
        player_chi = {
            "player1": 3.5,
            "player2": 2.0,
            "player3": 1.5,
            "player4": 0.8
        }
        
        valuation_changes = {
            "player1": 3.11,  # 311% like Indiana Fever
            "player2": 2.0,
            "player3": 1.5,
            "player4": 0.5
        }
        
        result = validator.valuation_jump_analysis(player_chi, valuation_changes)
        
        assert result.passed is True
        assert result.metric_value > 0.5
        assert "PASS" in result.message
        assert result.details["n_players"] == 4
    
    def test_no_correlation_fails(self):
        """Test that no correlation fails validation"""
        validator = BrandPortabilityValidator()
        
        player_chi = {
            "player1": 3.5,
            "player2": 2.0,
            "player3": 1.5
        }
        
        valuation_changes = {
            "player1": 0.5,  # Low valuation despite high chi
            "player2": 2.0,
            "player3": 3.0   # High valuation despite low chi
        }
        
        result = validator.valuation_jump_analysis(player_chi, valuation_changes)
        
        assert result.passed is False
        assert "FAIL" in result.message
    
    def test_empty_dicts_raises_error(self):
        """Test that empty dicts raise ValueError"""
        validator = BrandPortabilityValidator()
        
        with pytest.raises(ValueError, match="cannot be empty"):
            validator.valuation_jump_analysis({}, {})
    
    def test_no_matching_keys_raises_error(self):
        """Test that mismatched keys raise ValueError"""
        validator = BrandPortabilityValidator()
        
        player_chi = {"player1": 2.0}
        valuation_changes = {"player2": 1.5}
        
        with pytest.raises(ValueError, match="No matching player IDs"):
            validator.valuation_jump_analysis(player_chi, valuation_changes)


class TestRevenueMultipleConsistency:
    """Tests for revenue_multiple_consistency method"""
    
    def test_within_industry_standard_passes(self):
        """Test that multiples within 2-4x range pass"""
        validator = BrandPortabilityValidator()
        
        revenues = [50_000_000, 40_000_000, 30_000_000, 60_000_000]
        valuations = [150_000_000, 120_000_000, 90_000_000, 180_000_000]
        
        result = validator.revenue_multiple_consistency(revenues, valuations)
        
        assert result.passed is True
        assert 2.0 <= result.metric_value <= 4.0
        assert "PASS" in result.message
        assert result.details["n_teams"] == 4
    
    def test_below_range_fails(self):
        """Test that multiples below 2x fail"""
        validator = BrandPortabilityValidator()
        
        revenues = [50_000_000, 40_000_000]
        valuations = [60_000_000, 50_000_000]  # ~1.2x multiple
        
        result = validator.revenue_multiple_consistency(revenues, valuations)
        
        assert result.passed is False
        assert result.metric_value < 2.0
        assert "FAIL" in result.message
    
    def test_above_range_fails(self):
        """Test that multiples above 4x fail"""
        validator = BrandPortabilityValidator()
        
        revenues = [50_000_000, 40_000_000]
        valuations = [300_000_000, 250_000_000]  # ~6x multiple
        
        result = validator.revenue_multiple_consistency(revenues, valuations)
        
        assert result.passed is False
        assert result.metric_value > 4.0
        assert "FAIL" in result.message
    
    def test_empty_lists_raises_error(self):
        """Test that empty lists raise ValueError"""
        validator = BrandPortabilityValidator()
        
        with pytest.raises(ValueError, match="cannot be empty"):
            validator.revenue_multiple_consistency([], [])
    
    def test_mismatched_lengths_raises_error(self):
        """Test that mismatched lengths raise ValueError"""
        validator = BrandPortabilityValidator()
        
        with pytest.raises(ValueError, match="same length"):
            validator.revenue_multiple_consistency([1.0], [1.0, 2.0])
    
    def test_zero_revenue_raises_error(self):
        """Test that zero revenue raises ValueError"""
        validator = BrandPortabilityValidator()
        
        with pytest.raises(ValueError, match="must be positive"):
            validator.revenue_multiple_consistency([0.0, 50_000_000], [100_000_000, 150_000_000])


class TestMarketTierConsistency:
    """Tests for market_tier_consistency method"""
    
    def test_consistent_tiers_pass(self):
        """Test that consistent tier impacts pass validation"""
        validator = BrandPortabilityValidator()
        
        tier1 = [2.5, 2.7, 2.3, 2.6]
        tier2 = [2.4, 2.2, 2.5, 2.3]
        tier3 = [2.1, 2.3, 2.2, 2.4]
        
        result = validator.market_tier_consistency(tier1, tier2, tier3)
        
        assert result.passed is True
        assert result.metric_value <= 0.30
        assert "PASS" in result.message
        assert result.details["tier1_count"] == 4
    
    def test_inconsistent_tiers_fail(self):
        """Test that highly inconsistent tiers fail"""
        validator = BrandPortabilityValidator()
        
        tier1 = [5.0, 5.5, 4.8, 5.2]  # Very high
        tier2 = [2.0, 2.2, 1.9, 2.1]  # Medium
        tier3 = [0.5, 0.6, 0.4, 0.5]  # Very low
        
        result = validator.market_tier_consistency(tier1, tier2, tier3)
        
        assert result.passed is False
        assert result.metric_value > 0.30
        assert "FAIL" in result.message
    
    def test_empty_tier_raises_error(self):
        """Test that empty tier list raises ValueError"""
        validator = BrandPortabilityValidator()
        
        with pytest.raises(ValueError, match="must be non-empty"):
            validator.market_tier_consistency([], [1.0], [1.0])


class TestPeerComparison:
    """Tests for peer_comparison method"""
    
    def test_identifies_outliers(self):
        """Test that outliers are correctly identified"""
        validator = BrandPortabilityValidator()
        
        player_chi = {
            "player1": 2.0,
            "player2": 2.0,
            "player3": 2.0,
            "player4": 2.0,
            "player5": 2.0,
            "player6": 2.0,
            "player7": 10.0  # Clear outlier - very far from tight cluster
        }
        
        peer_groups = {
            "player1": "group_a",
            "player2": "group_a",
            "player3": "group_a",
            "player4": "group_a",
            "player5": "group_a",
            "player6": "group_a",
            "player7": "group_a"
        }
        
        results = validator.peer_comparison(player_chi, peer_groups)
        
        assert len(results) == 7
        
        # Find the outlier result
        outlier_results = [r for r in results if r.is_outlier]
        assert len(outlier_results) == 1
        assert outlier_results[0].value == 10.0
        assert "OUTLIER" in outlier_results[0].message
    
    def test_no_outliers_in_consistent_group(self):
        """Test that consistent group has no outliers"""
        validator = BrandPortabilityValidator()
        
        player_chi = {
            "player1": 2.0,
            "player2": 2.1,
            "player3": 2.2,
            "player4": 1.9,
            "player5": 2.0
        }
        
        peer_groups = {
            "player1": "group_a",
            "player2": "group_a",
            "player3": "group_a",
            "player4": "group_a",
            "player5": "group_a"
        }
        
        results = validator.peer_comparison(player_chi, peer_groups)
        
        outlier_results = [r for r in results if r.is_outlier]
        assert len(outlier_results) == 0
    
    def test_multiple_peer_groups(self):
        """Test with multiple peer groups"""
        validator = BrandPortabilityValidator()
        
        player_chi = {
            "player1": 2.0,
            "player2": 2.1,
            "player3": 1.0,
            "player4": 1.1
        }
        
        peer_groups = {
            "player1": "group_a",
            "player2": "group_a",
            "player3": "group_b",
            "player4": "group_b"
        }
        
        results = validator.peer_comparison(player_chi, peer_groups)
        
        assert len(results) == 4
        # Each group should be analyzed separately
        group_a_results = [r for r in results if "player1" in r.message or "player2" in r.message]
        group_b_results = [r for r in results if "player3" in r.message or "player4" in r.message]
        
        assert len(group_a_results) == 2
        assert len(group_b_results) == 2
    
    def test_single_player_group_no_outlier(self):
        """Test that single-player groups cannot be outliers"""
        validator = BrandPortabilityValidator()
        
        player_chi = {"player1": 2.0}
        peer_groups = {"player1": "group_a"}
        
        results = validator.peer_comparison(player_chi, peer_groups)
        
        assert len(results) == 1
        assert results[0].is_outlier is False
        assert "insufficient peer group size" in results[0].message
    
    def test_empty_dicts_raises_error(self):
        """Test that empty dicts raise ValueError"""
        validator = BrandPortabilityValidator()
        
        with pytest.raises(ValueError, match="cannot be empty"):
            validator.peer_comparison({}, {})
    
    def test_no_matching_keys_raises_error(self):
        """Test that mismatched keys raise ValueError"""
        validator = BrandPortabilityValidator()
        
        player_chi = {"player1": 2.0}
        peer_groups = {"player2": "group_a"}
        
        with pytest.raises(ValueError, match="No matching player IDs"):
            validator.peer_comparison(player_chi, peer_groups)


class TestCorrelationCalculation:
    """Tests for internal _calculate_correlation method"""
    
    def test_perfect_positive_correlation(self):
        """Test perfect positive correlation returns 1.0"""
        validator = BrandPortabilityValidator()
        
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]
        
        correlation = validator._calculate_correlation(x, y)
        
        assert correlation == pytest.approx(1.0, abs=0.01)
    
    def test_perfect_negative_correlation(self):
        """Test perfect negative correlation returns -1.0"""
        validator = BrandPortabilityValidator()
        
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [10.0, 8.0, 6.0, 4.0, 2.0]
        
        correlation = validator._calculate_correlation(x, y)
        
        assert correlation == pytest.approx(-1.0, abs=0.01)
    
    def test_no_correlation(self):
        """Test no correlation returns value near 0"""
        validator = BrandPortabilityValidator()
        
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [3.0, 1.0, 4.0, 2.0, 5.0]
        
        correlation = validator._calculate_correlation(x, y)
        
        # Should be close to 0 but not exactly due to random arrangement
        assert -0.6 < correlation < 0.6
    
    def test_constant_values_returns_zero(self):
        """Test that constant values return 0 correlation"""
        validator = BrandPortabilityValidator()
        
        x = [5.0, 5.0, 5.0, 5.0]
        y = [1.0, 2.0, 3.0, 4.0]
        
        correlation = validator._calculate_correlation(x, y)
        
        assert correlation == 0.0
    
    def test_mismatched_lengths_raises_error(self):
        """Test that mismatched lengths raise ValueError"""
        validator = BrandPortabilityValidator()
        
        with pytest.raises(ValueError, match="equal length"):
            validator._calculate_correlation([1.0, 2.0], [1.0, 2.0, 3.0])
    
    def test_empty_lists_raises_error(self):
        """Test that empty lists raise ValueError"""
        validator = BrandPortabilityValidator()
        
        with pytest.raises(ValueError, match="non-empty"):
            validator._calculate_correlation([], [])
