"""Merchandise sales estimator for player-specific revenue impact"""


class MerchandiseEstimator:
    """
    Estimate player-specific merchandise sales
    
    Formula: Merchandise Sales = (Scoring % × Salary % × Market Tier Factor) × League Revenue Baseline × 0.05
    
    The 0.05 multiplier represents the typical percentage of team revenue from merchandise sales.
    """
    
    def estimate_sales(
        self,
        scoring_percentile: float,
        salary_percentile: float,
        market_tier_factor: float,
        league_revenue_baseline: float
    ) -> float:
        """
        Estimate player-specific merchandise sales
        
        Args:
            scoring_percentile: Player's scoring percentile (0.0 to 1.0)
            salary_percentile: Player's salary percentile (0.0 to 1.0)
            market_tier_factor: Market adjustment (1.25, 1.0, or 0.85)
            league_revenue_baseline: Average team revenue from Forbes data
            
        Returns:
            Estimated annual merchandise sales attributable to player
            
        Raises:
            ValueError: If input values are out of valid ranges
            
        Example:
            >>> estimator = MerchandiseEstimator()
            >>> # Top 5% scorer, top 10% earner, Tier 1 market, $18M baseline
            >>> sales = estimator.estimate_sales(0.95, 0.90, 1.25, 18_000_000)
            >>> # Result: 0.95 × 0.90 × 1.25 × 18M × 0.05 = $963,750
        """
        # Validate input ranges
        if not 0.0 <= scoring_percentile <= 1.0:
            raise ValueError(
                f"scoring_percentile must be between 0.0 and 1.0, got {scoring_percentile}"
            )
        
        if not 0.0 <= salary_percentile <= 1.0:
            raise ValueError(
                f"salary_percentile must be between 0.0 and 1.0, got {salary_percentile}"
            )
        
        if market_tier_factor not in [0.85, 1.0, 1.25]:
            raise ValueError(
                f"market_tier_factor must be 0.85, 1.0, or 1.25, got {market_tier_factor}"
            )
        
        if league_revenue_baseline <= 0:
            raise ValueError(
                f"league_revenue_baseline must be positive, got {league_revenue_baseline}"
            )
        
        # Apply formula
        merchandise_sales = (
            scoring_percentile *
            salary_percentile *
            market_tier_factor *
            league_revenue_baseline *
            0.05
        )
        
        return merchandise_sales
