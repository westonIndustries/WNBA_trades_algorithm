"""Market Adjustment Factor (Ma) calculator for brand portability formula"""
from dataclasses import dataclass

from src.models import TeamData, MarketTierData


@dataclass
class MarketAdjustmentResult:
    """Result of market adjustment calculation"""
    adjustment_factor: float
    base_tier_factor: float
    dma_adjustment: float
    player_contribution_weight: float


class MarketAdjustmentCalculator:
    """
    Calculate market adjustment factor (Ma)
    
    Ma is a weight based on team value data to measure actual player contribution,
    not just city size. It incorporates:
    - Base market tier factor (1.25 for Tier 1, 1.0 for Tier 2, 0.85 for Tier 3)
    - DMA ranking adjustment to account for market reach
    - Player contribution weight to normalize across markets
    
    This ensures fair comparison between large and small markets.
    """
    
    def calculate(
        self,
        team_data: TeamData,
        market_tier_data: MarketTierData,
        player_contribution_weight: float
    ) -> MarketAdjustmentResult:
        """
        Calculate market adjustment factor
        
        Steps:
        1. Get base market tier factor (1.25, 1.0, or 0.85)
        2. Apply DMA ranking adjustment
        3. Factor in player contribution weight
        4. Normalize to ensure fair comparison across markets
        
        Args:
            team_data: Team data including market tier and DMA ranking
            market_tier_data: Market tier classification with adjustment factors
            player_contribution_weight: Player's contribution weight (0.0 to 1.0)
            
        Returns:
            MarketAdjustmentResult with breakdown
            
        Raises:
            ValueError: If market tier is invalid or player contribution weight is out of range
        """
        # Validate inputs
        if team_data.market_tier not in [1, 2, 3]:
            raise ValueError(
                f"Invalid market tier: {team_data.market_tier}. Must be 1, 2, or 3."
            )
        
        if not 0.0 <= player_contribution_weight <= 1.0:
            raise ValueError(
                f"Player contribution weight must be between 0.0 and 1.0, "
                f"got {player_contribution_weight}"
            )
        
        # Get base market tier factor
        base_tier_factor = self._get_base_tier_factor(market_tier_data)
        
        # Calculate DMA ranking adjustment
        # Lower DMA ranking = larger market = higher adjustment
        # DMA rankings typically range from 1 (largest) to 210 (smallest)
        # We normalize to a 0.5 to 1.5 range
        dma_adjustment = self._calculate_dma_adjustment(team_data.dma_ranking)
        
        # Calculate final adjustment factor
        # Formula: Ma = base_tier_factor × dma_adjustment × (1 + player_contribution_weight × 0.5)
        # The player contribution weight adds up to 50% boost for high-impact players
        contribution_multiplier = 1.0 + (player_contribution_weight * 0.5)
        
        adjustment_factor = base_tier_factor * dma_adjustment * contribution_multiplier
        
        return MarketAdjustmentResult(
            adjustment_factor=adjustment_factor,
            base_tier_factor=base_tier_factor,
            dma_adjustment=dma_adjustment,
            player_contribution_weight=player_contribution_weight
        )
    
    def _get_base_tier_factor(self, market_tier_data: MarketTierData) -> float:
        """
        Get base market tier factor from market tier data
        
        Args:
            market_tier_data: Market tier classification
            
        Returns:
            Base tier factor (1.25, 1.0, or 0.85)
        """
        return market_tier_data.adjustment_factor
    
    def _calculate_dma_adjustment(self, dma_ranking: int) -> float:
        """
        Calculate DMA ranking adjustment factor
        
        DMA (Designated Market Area) rankings measure market size.
        Lower ranking = larger market.
        
        We use a logarithmic scale to normalize DMA rankings:
        - DMA 1 (New York) → adjustment ≈ 1.5
        - DMA 50 (mid-size) → adjustment ≈ 1.0
        - DMA 210 (smallest) → adjustment ≈ 0.5
        
        Formula: adjustment = 1.5 - (log(dma_ranking) / log(210)) × 1.0
        
        Args:
            dma_ranking: DMA ranking (1 to 210)
            
        Returns:
            DMA adjustment factor (0.5 to 1.5)
        """
        import math
        
        # Validate DMA ranking
        if dma_ranking < 1:
            raise ValueError(f"DMA ranking must be at least 1, got {dma_ranking}")
        
        # Cap at 210 (approximate number of DMAs in US)
        dma_ranking = min(dma_ranking, 210)
        
        # Logarithmic scaling
        # log(1) = 0 → adjustment = 1.5
        # log(210) / log(210) = 1 → adjustment = 0.5
        adjustment = 1.5 - (math.log(dma_ranking) / math.log(210)) * 1.0
        
        # Ensure bounds
        return max(0.5, min(1.5, adjustment))
