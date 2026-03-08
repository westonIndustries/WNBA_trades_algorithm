"""Unit tests for MarketAdjustmentCalculator"""
import pytest
import math

from src.calculators import MarketAdjustmentCalculator, MarketAdjustmentResult
from src.models import TeamData, TeamAnnualRecord, MarketTierData


class TestMarketAdjustmentCalculator:
    """Unit tests for MarketAdjustmentCalculator"""
    
    def test_calculate_tier_1_market(self):
        """Test market adjustment calculation for Tier 1 (large) market"""
        calculator = MarketAdjustmentCalculator()
        
        # Create Tier 1 market data (e.g., New York)
        market_tier_data = MarketTierData(
            tier=1,
            adjustment_factor=1.25,
            teams=["NY"]
        )
        
        team_data = TeamData(
            team_id="NY",
            team_name="New York Liberty",
            market_tier=1,
            dma_ranking=1,  # Largest market
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=400_000_000,
                    revenue=30_000_000,
                    attendance_avg=15000,
                    points_per_game=85.0
                )
            ]
        )
        
        # Calculate with moderate player contribution
        result = calculator.calculate(team_data, market_tier_data, 0.5)
        
        # Verify result structure
        assert isinstance(result, MarketAdjustmentResult)
        
        # Verify base tier factor for Tier 1
        assert result.base_tier_factor == 1.25
        
        # Verify DMA adjustment for largest market (should be close to 1.5)
        assert result.dma_adjustment > 1.4
        assert result.dma_adjustment <= 1.5
        
        # Verify player contribution weight
        assert result.player_contribution_weight == 0.5
        
        # Verify adjustment factor is positive and reasonable
        assert result.adjustment_factor > 0
        # For Tier 1, DMA 1, weight 0.5: should be around 1.25 * 1.5 * 1.25 = 2.34
        assert result.adjustment_factor > 2.0
    
    def test_calculate_tier_2_market(self):
        """Test market adjustment calculation for Tier 2 (mid-size) market"""
        calculator = MarketAdjustmentCalculator()
        
        # Create Tier 2 market data (e.g., Seattle)
        market_tier_data = MarketTierData(
            tier=2,
            adjustment_factor=1.0,
            teams=["SEA"]
        )
        
        team_data = TeamData(
            team_id="SEA",
            team_name="Seattle Storm",
            market_tier=2,
            dma_ranking=13,  # Mid-size market
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=250_000_000,
                    revenue=20_000_000,
                    attendance_avg=12000,
                    points_per_game=82.0
                )
            ]
        )
        
        # Calculate with moderate player contribution
        result = calculator.calculate(team_data, market_tier_data, 0.5)
        
        # Verify base tier factor for Tier 2
        assert result.base_tier_factor == 1.0
        
        # Verify DMA adjustment for mid-size market
        assert 1.0 <= result.dma_adjustment <= 1.5
        
        # Verify adjustment factor
        assert result.adjustment_factor > 0
        # For Tier 2, should be lower than Tier 1
        assert result.adjustment_factor < 2.0
    
    def test_calculate_tier_3_market(self):
        """Test market adjustment calculation for Tier 3 (smaller) market"""
        calculator = MarketAdjustmentCalculator()
        
        # Create Tier 3 market data (e.g., Connecticut)
        market_tier_data = MarketTierData(
            tier=3,
            adjustment_factor=0.85,
            teams=["CONN"]
        )
        
        team_data = TeamData(
            team_id="CONN",
            team_name="Connecticut Sun",
            market_tier=3,
            dma_ranking=30,  # Smaller market
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=190_000_000,
                    revenue=15_000_000,
                    attendance_avg=9000,
                    points_per_game=80.0
                )
            ]
        )
        
        # Calculate with moderate player contribution
        result = calculator.calculate(team_data, market_tier_data, 0.5)
        
        # Verify base tier factor for Tier 3
        assert result.base_tier_factor == 0.85
        
        # Verify DMA adjustment
        assert 0.5 <= result.dma_adjustment <= 1.5
        
        # Verify adjustment factor
        assert result.adjustment_factor > 0
        # For Tier 3, should be lower than Tier 2
        assert result.adjustment_factor < 1.5
    
    def test_dma_ranking_adjustments(self):
        """Test that DMA ranking adjustments work correctly"""
        calculator = MarketAdjustmentCalculator()
        
        market_tier_data = MarketTierData(
            tier=2,
            adjustment_factor=1.0,
            teams=["TEAM1", "TEAM2", "TEAM3"]
        )
        
        # Test three different DMA rankings
        dma_rankings = [1, 50, 200]
        results = []
        
        for dma in dma_rankings:
            team_data = TeamData(
                team_id=f"TEAM{dma}",
                team_name=f"Team {dma}",
                market_tier=2,
                dma_ranking=dma,
                annual_records=[
                    TeamAnnualRecord(
                        year=2024,
                        valuation=200_000_000,
                        revenue=18_000_000,
                        attendance_avg=10000,
                        points_per_game=81.0
                    )
                ]
            )
            
            result = calculator.calculate(team_data, market_tier_data, 0.5)
            results.append((dma, result))
        
        # Verify DMA 1 has highest adjustment
        assert results[0][1].dma_adjustment >= results[1][1].dma_adjustment
        assert results[1][1].dma_adjustment >= results[2][1].dma_adjustment
        
        # Verify DMA adjustments are within bounds
        for dma, result in results:
            assert 0.5 <= result.dma_adjustment <= 1.5
    
    def test_player_contribution_weight_integration(self):
        """Test that player contribution weight affects adjustment factor"""
        calculator = MarketAdjustmentCalculator()
        
        market_tier_data = MarketTierData(
            tier=2,
            adjustment_factor=1.0,
            teams=["TEAM1"]
        )
        
        team_data = TeamData(
            team_id="TEAM1",
            team_name="Test Team",
            market_tier=2,
            dma_ranking=25,
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=200_000_000,
                    revenue=18_000_000,
                    attendance_avg=10000,
                    points_per_game=81.0
                )
            ]
        )
        
        # Test with different player contribution weights
        weights = [0.0, 0.25, 0.5, 0.75, 1.0]
        results = []
        
        for weight in weights:
            result = calculator.calculate(team_data, market_tier_data, weight)
            results.append((weight, result))
        
        # Verify higher weights result in higher adjustment factors
        for i in range(len(results) - 1):
            assert results[i + 1][1].adjustment_factor >= results[i][1].adjustment_factor, (
                f"Weight {results[i + 1][0]} should have higher adjustment "
                f"than weight {results[i][0]}"
            )
        
        # Verify the formula: Ma = base × dma × (1 + weight × 0.5)
        for weight, result in results:
            expected = (
                result.base_tier_factor *
                result.dma_adjustment *
                (1.0 + weight * 0.5)
            )
            assert abs(result.adjustment_factor - expected) < 0.001
    
    def test_tier_comparison_same_dma(self):
        """Test that tier ordering is maintained for same DMA ranking"""
        calculator = MarketAdjustmentCalculator()
        
        dma_ranking = 25
        player_weight = 0.5
        
        results = {}
        for tier in [1, 2, 3]:
            tier_to_factor = {1: 1.25, 2: 1.0, 3: 0.85}
            
            market_tier_data = MarketTierData(
                tier=tier,
                adjustment_factor=tier_to_factor[tier],
                teams=[f"TEAM{tier}"]
            )
            
            team_data = TeamData(
                team_id=f"TEAM{tier}",
                team_name=f"Team {tier}",
                market_tier=tier,
                dma_ranking=dma_ranking,
                annual_records=[
                    TeamAnnualRecord(
                        year=2024,
                        valuation=200_000_000,
                        revenue=18_000_000,
                        attendance_avg=10000,
                        points_per_game=81.0
                    )
                ]
            )
            
            results[tier] = calculator.calculate(team_data, market_tier_data, player_weight)
        
        # Verify tier ordering: Tier 1 > Tier 2 > Tier 3
        assert results[1].adjustment_factor > results[2].adjustment_factor
        assert results[2].adjustment_factor > results[3].adjustment_factor
    
    def test_invalid_market_tier_raises_error(self):
        """Test that invalid market tier raises ValueError"""
        calculator = MarketAdjustmentCalculator()
        
        market_tier_data = MarketTierData(
            tier=4,  # Invalid
            adjustment_factor=1.0,
            teams=["TEAM1"]
        )
        
        team_data = TeamData(
            team_id="TEAM1",
            team_name="Test Team",
            market_tier=4,  # Invalid
            dma_ranking=25,
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=200_000_000,
                    revenue=18_000_000,
                    attendance_avg=10000,
                    points_per_game=81.0
                )
            ]
        )
        
        with pytest.raises(ValueError, match="Invalid market tier"):
            calculator.calculate(team_data, market_tier_data, 0.5)
    
    def test_invalid_player_weight_raises_error(self):
        """Test that invalid player contribution weight raises ValueError"""
        calculator = MarketAdjustmentCalculator()
        
        market_tier_data = MarketTierData(
            tier=2,
            adjustment_factor=1.0,
            teams=["TEAM1"]
        )
        
        team_data = TeamData(
            team_id="TEAM1",
            team_name="Test Team",
            market_tier=2,
            dma_ranking=25,
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=200_000_000,
                    revenue=18_000_000,
                    attendance_avg=10000,
                    points_per_game=81.0
                )
            ]
        )
        
        # Test with weight > 1.0
        with pytest.raises(ValueError, match="Player contribution weight must be between"):
            calculator.calculate(team_data, market_tier_data, 1.5)
        
        # Test with weight < 0.0
        with pytest.raises(ValueError, match="Player contribution weight must be between"):
            calculator.calculate(team_data, market_tier_data, -0.1)
    
    def test_dma_adjustment_formula(self):
        """Test the DMA adjustment formula directly"""
        calculator = MarketAdjustmentCalculator()
        
        # Test specific DMA rankings
        test_cases = [
            (1, 1.5),      # Largest market should be close to 1.5
            (210, 0.5),    # Smallest market should be close to 0.5
        ]
        
        for dma, expected_approx in test_cases:
            adjustment = calculator._calculate_dma_adjustment(dma)
            
            # Verify bounds
            assert 0.5 <= adjustment <= 1.5
            
            # Verify approximate expected value
            assert abs(adjustment - expected_approx) < 0.1, (
                f"DMA {dma} adjustment {adjustment} should be close to {expected_approx}"
            )
    
    def test_dma_adjustment_invalid_ranking(self):
        """Test that invalid DMA ranking raises ValueError"""
        calculator = MarketAdjustmentCalculator()
        
        # DMA ranking must be at least 1
        with pytest.raises(ValueError, match="DMA ranking must be at least 1"):
            calculator._calculate_dma_adjustment(0)
        
        with pytest.raises(ValueError, match="DMA ranking must be at least 1"):
            calculator._calculate_dma_adjustment(-5)
    
    def test_real_world_scenario_caitlin_clark(self):
        """Test with real-world scenario: high-impact player in mid-tier market"""
        calculator = MarketAdjustmentCalculator()
        
        # Indiana Fever - Tier 2 market
        market_tier_data = MarketTierData(
            tier=2,
            adjustment_factor=1.0,
            teams=["IND"]
        )
        
        team_data = TeamData(
            team_id="IND",
            team_name="Indiana Fever",
            market_tier=2,
            dma_ranking=26,  # Indianapolis
            annual_records=[
                TeamAnnualRecord(
                    year=2024,
                    valuation=250_000_000,
                    revenue=32_000_000,
                    attendance_avg=17000,
                    points_per_game=84.5
                )
            ]
        )
        
        # High player contribution weight for star player
        result = calculator.calculate(team_data, market_tier_data, 0.8)
        
        # Verify result
        assert result.base_tier_factor == 1.0
        assert 0.5 <= result.dma_adjustment <= 1.5
        assert result.player_contribution_weight == 0.8
        
        # High contribution weight should boost adjustment factor
        assert result.adjustment_factor > 1.0
        
        # Verify formula
        expected = result.base_tier_factor * result.dma_adjustment * (1.0 + 0.8 * 0.5)
        assert abs(result.adjustment_factor - expected) < 0.001
