"""Unit tests for estimation layer"""
import pytest

from src.estimators import (
    MerchandiseEstimator,
    TVRatingEstimator,
    TicketPremiumEstimator,
    PlayerRevenueAttributor
)


class TestMerchandiseEstimator:
    """Unit tests for MerchandiseEstimator"""
    
    def test_estimate_sales_basic(self):
        """Test basic merchandise sales estimation"""
        estimator = MerchandiseEstimator()
        
        # Top 5% scorer, top 10% earner, Tier 1 market, $18M baseline
        sales = estimator.estimate_sales(0.95, 0.90, 1.25, 18_000_000)
        
        # Expected: 0.95 × 0.90 × 1.25 × 18M × 0.05 = 963,750
        expected = 0.95 * 0.90 * 1.25 * 18_000_000 * 0.05
        assert abs(sales - expected) < 1.0
    
    def test_estimate_sales_tier_2_market(self):
        """Test merchandise sales in Tier 2 market"""
        estimator = MerchandiseEstimator()
        
        sales = estimator.estimate_sales(0.80, 0.75, 1.0, 15_000_000)
        
        # Expected: 0.80 × 0.75 × 1.0 × 15M × 0.05 = 450,000
        expected = 0.80 * 0.75 * 1.0 * 15_000_000 * 0.05
        assert abs(sales - expected) < 1.0
    
    def test_estimate_sales_tier_3_market(self):
        """Test merchandise sales in Tier 3 market"""
        estimator = MerchandiseEstimator()
        
        sales = estimator.estimate_sales(0.70, 0.60, 0.85, 12_000_000)
        
        # Expected: 0.70 × 0.60 × 0.85 × 12M × 0.05 = 214,200
        expected = 0.70 * 0.60 * 0.85 * 12_000_000 * 0.05
        assert abs(sales - expected) < 1.0
    
    def test_estimate_sales_invalid_scoring_percentile(self):
        """Test error handling for invalid scoring percentile"""
        estimator = MerchandiseEstimator()
        
        with pytest.raises(ValueError) as exc_info:
            estimator.estimate_sales(1.5, 0.90, 1.25, 18_000_000)
        
        assert "scoring_percentile" in str(exc_info.value)
    
    def test_estimate_sales_invalid_market_tier(self):
        """Test error handling for invalid market tier factor"""
        estimator = MerchandiseEstimator()
        
        with pytest.raises(ValueError) as exc_info:
            estimator.estimate_sales(0.95, 0.90, 1.5, 18_000_000)
        
        assert "market_tier_factor" in str(exc_info.value)


class TestTVRatingEstimator:
    """Unit tests for TVRatingEstimator"""
    
    def test_estimate_impact_basic(self):
        """Test basic TV rating impact estimation"""
        estimator = TVRatingEstimator()
        
        # Top scorer, high salary, strong social media, 20% growth, large market
        impact = estimator.estimate_impact(0.95, 0.90, 0.85, 0.20, 1.3)
        
        # Star power: (0.95×0.4) + (0.90×0.3) + (0.85×0.3) = 0.905
        star_power = (0.95 * 0.4) + (0.90 * 0.3) + (0.85 * 0.3)
        expected = star_power * 0.20 * 1.3
        
        assert abs(impact - expected) < 0.001
    
    def test_estimate_impact_star_power_calculation(self):
        """Test star power score calculation"""
        estimator = TVRatingEstimator()
        
        # Equal values should produce weighted average
        impact = estimator.estimate_impact(0.5, 0.5, 0.5, 1.0, 1.0)
        
        # Star power: (0.5×0.4) + (0.5×0.3) + (0.5×0.3) = 0.5
        # Impact: 0.5 × 1.0 × 1.0 = 0.5
        assert abs(impact - 0.5) < 0.001
    
    def test_estimate_impact_invalid_social_media(self):
        """Test error handling for invalid social media index"""
        estimator = TVRatingEstimator()
        
        with pytest.raises(ValueError) as exc_info:
            estimator.estimate_impact(0.95, 0.90, 1.5, 0.20, 1.3)
        
        assert "social_media_index" in str(exc_info.value)
    
    def test_estimate_impact_invalid_market_reach(self):
        """Test error handling for invalid market reach factor"""
        estimator = TVRatingEstimator()
        
        with pytest.raises(ValueError) as exc_info:
            estimator.estimate_impact(0.95, 0.90, 0.85, 0.20, 2.0)
        
        assert "market_reach_factor" in str(exc_info.value)


class TestTicketPremiumEstimator:
    """Unit tests for TicketPremiumEstimator"""
    
    def test_estimate_premium_basic(self):
        """Test basic ticket premium estimation"""
        estimator = TicketPremiumEstimator()
        
        # Caitlin Clark impact: 17K vs 9K attendance, $50 tickets, 35% attribution, 1.5x star power, 20 games
        premium = estimator.estimate_premium(17000, 9000, 50, 0.35, 1.5, 20)
        
        # Attendance diff: 8,000
        # Attribution: 0.35 × 1.5 = 0.525
        # Premium: 8,000 × $50 × 0.525 × 20 = $4,200,000
        expected = 8000 * 50 * 0.35 * 1.5 * 20
        assert abs(premium - expected) < 1.0
    
    def test_estimate_premium_no_attendance_increase(self):
        """Test ticket premium when attendance doesn't change"""
        estimator = TicketPremiumEstimator()
        
        premium = estimator.estimate_premium(10000, 10000, 50, 0.35, 1.5, 20)
        
        # No attendance difference = no premium
        assert premium == 0.0
    
    def test_estimate_premium_attendance_decrease(self):
        """Test ticket premium when attendance decreases"""
        estimator = TicketPremiumEstimator()
        
        premium = estimator.estimate_premium(8000, 10000, 50, 0.35, 1.5, 20)
        
        # Negative attendance difference = negative premium
        expected = -2000 * 50 * 0.35 * 1.5 * 20
        assert abs(premium - expected) < 1.0
        assert premium < 0
    
    def test_estimate_premium_invalid_attendance(self):
        """Test error handling for invalid attendance"""
        estimator = TicketPremiumEstimator()
        
        with pytest.raises(ValueError) as exc_info:
            estimator.estimate_premium(-1000, 9000, 50, 0.35, 1.5, 20)
        
        assert "attendance_with_player" in str(exc_info.value)
    
    def test_estimate_premium_invalid_star_power(self):
        """Test error handling for invalid star power multiplier"""
        estimator = TicketPremiumEstimator()
        
        with pytest.raises(ValueError) as exc_info:
            estimator.estimate_premium(17000, 9000, 50, 0.35, 3.0, 20)
        
        assert "star_power_multiplier" in str(exc_info.value)


class TestPlayerRevenueAttributor:
    """Unit tests for PlayerRevenueAttributor"""
    
    def test_calculate_attribution_basic(self):
        """Test basic player revenue attribution"""
        attributor = PlayerRevenueAttributor()
        
        # Caitlin Clark: $22.9M revenue increase, 19.2 PPG / 84.5 team PPG
        # $76K salary / $1.46M cap, 40/40 games, 35 MPG
        impact = attributor.calculate_attribution(
            22_900_000, 19.2, 84.5, 76_000, 1_460_000, 40, 40, 35
        )
        
        # Performance weight: (19.2/84.5)×0.6 + (76K/1.46M)×0.4 = 0.157
        perf_weight = (19.2 / 84.5) * 0.6 + (76_000 / 1_460_000) * 0.4
        # Playing time: (40/40) × (35/40) = 0.875
        playing_time = (40 / 40) * (35 / 40)
        # Impact: $22.9M × 0.157 × 0.875
        expected = 22_900_000 * perf_weight * playing_time
        
        assert abs(impact - expected) < 1000.0  # Allow $1000 rounding error
    
    def test_calculate_attribution_partial_season(self):
        """Test attribution for player who played partial season"""
        attributor = PlayerRevenueAttributor()
        
        # Player played 20 out of 40 games
        impact = attributor.calculate_attribution(
            10_000_000, 15.0, 80.0, 100_000, 1_500_000, 20, 40, 30
        )
        
        # Performance weight: (15/80)×0.6 + (100K/1.5M)×0.4 = 0.139
        perf_weight = (15.0 / 80.0) * 0.6 + (100_000 / 1_500_000) * 0.4
        # Playing time: (20/40) × (30/40) = 0.375
        playing_time = (20 / 40) * (30 / 40)
        # Impact: $10M × 0.139 × 0.375
        expected = 10_000_000 * perf_weight * playing_time
        
        assert abs(impact - expected) < 1000.0
    
    def test_calculate_attribution_zero_revenue_change(self):
        """Test attribution when revenue doesn't change"""
        attributor = PlayerRevenueAttributor()
        
        impact = attributor.calculate_attribution(
            0, 15.0, 80.0, 100_000, 1_500_000, 40, 40, 30
        )
        
        assert impact == 0.0
    
    def test_calculate_attribution_negative_revenue_change(self):
        """Test attribution when revenue decreases"""
        attributor = PlayerRevenueAttributor()
        
        impact = attributor.calculate_attribution(
            -5_000_000, 15.0, 80.0, 100_000, 1_500_000, 40, 40, 30
        )
        
        # Should produce negative attribution
        assert impact < 0
    
    def test_calculate_attribution_invalid_team_ppg(self):
        """Test error handling for invalid team PPG"""
        attributor = PlayerRevenueAttributor()
        
        with pytest.raises(ValueError) as exc_info:
            attributor.calculate_attribution(
                10_000_000, 15.0, 0, 100_000, 1_500_000, 40, 40, 30
            )
        
        assert "team_ppg" in str(exc_info.value)
    
    def test_calculate_attribution_invalid_games_played(self):
        """Test error handling for games played exceeding total"""
        attributor = PlayerRevenueAttributor()
        
        with pytest.raises(ValueError) as exc_info:
            attributor.calculate_attribution(
                10_000_000, 15.0, 80.0, 100_000, 1_500_000, 50, 40, 30
            )
        
        assert "games_played" in str(exc_info.value)
    
    def test_calculate_attribution_invalid_minutes(self):
        """Test error handling for minutes exceeding 40"""
        attributor = PlayerRevenueAttributor()
        
        with pytest.raises(ValueError) as exc_info:
            attributor.calculate_attribution(
                10_000_000, 15.0, 80.0, 100_000, 1_500_000, 40, 40, 45
            )
        
        assert "minutes_per_game" in str(exc_info.value)
