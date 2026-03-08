"""TV rating impact estimator for player-specific viewership effects"""


class TVRatingEstimator:
    """
    Estimate player-specific TV rating impact
    
    Formula: TV Rating Impact = (Star Power Score) × (League Viewership Growth) × (Market Reach Factor)
    Star Power = (Scoring % × 0.4) + (Salary % × 0.3) + (Social Media Index × 0.3)
    
    The star power formula weights on-court performance (40%), salary as brand proxy (30%),
    and social media engagement (30%).
    """
    
    def estimate_impact(
        self,
        scoring_percentile: float,
        salary_percentile: float,
        social_media_index: float,
        league_viewership_growth: float,
        market_reach_factor: float
    ) -> float:
        """
        Estimate player-specific TV rating impact
        
        Args:
            scoring_percentile: Player's scoring percentile (0.0 to 1.0)
            salary_percentile: Player's salary percentile (0.0 to 1.0)
            social_media_index: Normalized social media engagement (0.0 to 1.0)
            league_viewership_growth: Year-over-year viewership growth rate
            market_reach_factor: Based on DMA ranking (0.5 to 1.5)
            
        Returns:
            Estimated TV rating impact in dollars
            
        Raises:
            ValueError: If input values are out of valid ranges
            
        Example:
            >>> estimator = TVRatingEstimator()
            >>> # Top scorer, high salary, strong social media, 20% growth, large market
            >>> impact = estimator.estimate_impact(0.95, 0.90, 0.85, 0.20, 1.3)
            >>> # Star power: (0.95×0.4) + (0.90×0.3) + (0.85×0.3) = 0.905
            >>> # Impact: 0.905 × 0.20 × 1.3 = 0.2353 (normalized score)
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
        
        if not 0.0 <= social_media_index <= 1.0:
            raise ValueError(
                f"social_media_index must be between 0.0 and 1.0, got {social_media_index}"
            )
        
        if not 0.5 <= market_reach_factor <= 1.5:
            raise ValueError(
                f"market_reach_factor must be between 0.5 and 1.5, got {market_reach_factor}"
            )
        
        # Calculate star power score
        star_power = (
            (scoring_percentile * 0.4) +
            (salary_percentile * 0.3) +
            (social_media_index * 0.3)
        )
        
        # Calculate TV rating impact
        tv_impact = star_power * league_viewership_growth * market_reach_factor
        
        return tv_impact
