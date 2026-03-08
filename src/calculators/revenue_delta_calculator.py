"""Revenue Delta (ΔRm) calculator for brand portability formula"""
from dataclasses import dataclass
from typing import Dict

from src.models import PlayerData, TeamData, LeagueData
from src.estimators import (
    MerchandiseEstimator,
    TVRatingEstimator,
    TicketPremiumEstimator
)


@dataclass
class RevenueDeltaResult:
    """Result of revenue delta calculation"""
    total_delta: float
    career_avg_revenue: float
    new_city_revenue: float
    components: Dict[str, float]  # merchandise, tv_rating, ticket_premium


class RevenueDeltaCalculator:
    """
    Calculate revenue delta (ΔRm): new city revenue minus career average revenue
    
    ΔRm represents the change in player-specific revenue in the new city compared
    to their career average. Components include:
    - Merchandise sales changes
    - TV ratings impact
    - Ticket premium from attendance
    
    Formula: ΔRm = New City Revenue - Career Average Revenue
    """
    
    def __init__(
        self,
        merchandise_estimator: MerchandiseEstimator,
        tv_rating_estimator: TVRatingEstimator,
        ticket_premium_estimator: TicketPremiumEstimator
    ):
        """
        Initialize RevenueDeltaCalculator with estimator dependencies
        
        Args:
            merchandise_estimator: Estimator for merchandise sales
            tv_rating_estimator: Estimator for TV rating impact
            ticket_premium_estimator: Estimator for ticket premium
        """
        self.merchandise_estimator = merchandise_estimator
        self.tv_rating_estimator = tv_rating_estimator
        self.ticket_premium_estimator = ticket_premium_estimator
    
    def calculate(
        self,
        player_data: PlayerData,
        new_team_data: TeamData,
        league_data: LeagueData
    ) -> RevenueDeltaResult:
        """
        Calculate revenue delta: new city revenue minus career average revenue
        
        Steps:
        1. Calculate career average revenue metrics
        2. Estimate new city-specific revenue impact
        3. Compute delta between new city and career average
        
        Args:
            player_data: Player career statistics and performance
            new_team_data: New team's market and performance data
            league_data: League-wide averages and trends
            
        Returns:
            RevenueDeltaResult with breakdown of components
            
        Raises:
            ValueError: If player has no career data or invalid inputs
        """
        if not player_data.annual_records:
            raise ValueError("Player must have at least one year of career data")
        
        if not new_team_data.annual_records:
            raise ValueError("New team must have historical data")
        
        if not league_data.annual_records:
            raise ValueError("League data must have historical records")
        
        # Calculate career average revenue components
        career_merchandise = self._calculate_career_avg_merchandise(
            player_data, league_data
        )
        career_tv_rating = self._calculate_career_avg_tv_rating(
            player_data, league_data
        )
        career_ticket_premium = self._calculate_career_avg_ticket_premium(
            player_data, league_data
        )
        
        career_avg_revenue = career_merchandise + career_tv_rating + career_ticket_premium
        
        # Estimate new city revenue components
        new_merchandise = self._estimate_new_city_merchandise(
            player_data, new_team_data, league_data
        )
        new_tv_rating = self._estimate_new_city_tv_rating(
            player_data, new_team_data, league_data
        )
        new_ticket_premium = self._estimate_new_city_ticket_premium(
            player_data, new_team_data, league_data
        )
        
        new_city_revenue = new_merchandise + new_tv_rating + new_ticket_premium
        
        # Calculate delta
        total_delta = new_city_revenue - career_avg_revenue
        
        # Component breakdown
        components = {
            "merchandise": new_merchandise - career_merchandise,
            "tv_rating": new_tv_rating - career_tv_rating,
            "ticket_premium": new_ticket_premium - career_ticket_premium
        }
        
        return RevenueDeltaResult(
            total_delta=total_delta,
            career_avg_revenue=career_avg_revenue,
            new_city_revenue=new_city_revenue,
            components=components
        )
    
    def _calculate_career_avg_merchandise(
        self,
        player_data: PlayerData,
        league_data: LeagueData
    ) -> float:
        """Calculate career average merchandise sales"""
        total_merchandise = 0.0
        count = 0
        
        for record in player_data.annual_records:
            # Get league baseline for this year
            league_record = self._get_league_record(league_data, record.year)
            if not league_record:
                continue
            
            # Estimate merchandise for this year
            # Use scoring percentile from record, assume mid-tier market (1.0)
            scoring_pct = record.scoring_percentile if record.scoring_percentile else 0.5
            salary_pct = 0.5  # Default if not available
            
            merchandise = self.merchandise_estimator.estimate_sales(
                scoring_percentile=scoring_pct,
                salary_percentile=salary_pct,
                market_tier_factor=1.0,  # Neutral market for career average
                league_revenue_baseline=league_record.avg_salary * 12  # Rough baseline
            )
            
            total_merchandise += merchandise
            count += 1
        
        return total_merchandise / count if count > 0 else 0.0
    
    def _calculate_career_avg_tv_rating(
        self,
        player_data: PlayerData,
        league_data: LeagueData
    ) -> float:
        """Calculate career average TV rating impact"""
        # Simplified: return normalized score based on career performance
        # In production, this would use actual viewership data
        total_impact = 0.0
        count = 0
        
        for record in player_data.annual_records:
            scoring_pct = record.scoring_percentile if record.scoring_percentile else 0.5
            salary_pct = 0.5
            social_media = 0.5  # Default
            
            impact = self.tv_rating_estimator.estimate_impact(
                scoring_percentile=scoring_pct,
                salary_percentile=salary_pct,
                social_media_index=social_media,
                league_viewership_growth=0.1,  # Assume 10% growth
                market_reach_factor=1.0  # Neutral market
            )
            
            total_impact += impact
            count += 1
        
        return total_impact / count if count > 0 else 0.0
    
    def _calculate_career_avg_ticket_premium(
        self,
        player_data: PlayerData,
        league_data: LeagueData
    ) -> float:
        """Calculate career average ticket premium"""
        # Simplified: return average based on career performance
        total_premium = 0.0
        count = 0
        
        for record in player_data.annual_records:
            # Estimate ticket premium contribution
            premium = self.ticket_premium_estimator.estimate_premium(
                attendance_with_player=10000,  # Default baseline
                attendance_without_player=9000,
                avg_ticket_price=50,
                player_performance_weight=0.3,
                star_power_multiplier=1.0,
                home_games=20
            )
            
            total_premium += premium
            count += 1
        
        return total_premium / count if count > 0 else 0.0
    
    def _estimate_new_city_merchandise(
        self,
        player_data: PlayerData,
        new_team_data: TeamData,
        league_data: LeagueData
    ) -> float:
        """Estimate merchandise sales in new city"""
        # Use most recent player performance
        latest_record = player_data.annual_records[-1]
        latest_team_record = new_team_data.annual_records[-1]
        
        scoring_pct = latest_record.scoring_percentile if latest_record.scoring_percentile else 0.5
        salary_pct = 0.5
        
        # Get market tier factor
        market_tier_factor = self._get_market_tier_factor(new_team_data.market_tier)
        
        # Use team revenue as baseline
        league_baseline = latest_team_record.revenue if latest_team_record.revenue > 0 else 15_000_000
        
        return self.merchandise_estimator.estimate_sales(
            scoring_percentile=scoring_pct,
            salary_percentile=salary_pct,
            market_tier_factor=market_tier_factor,
            league_revenue_baseline=league_baseline
        )
    
    def _estimate_new_city_tv_rating(
        self,
        player_data: PlayerData,
        new_team_data: TeamData,
        league_data: LeagueData
    ) -> float:
        """Estimate TV rating impact in new city"""
        latest_record = player_data.annual_records[-1]
        
        scoring_pct = latest_record.scoring_percentile if latest_record.scoring_percentile else 0.5
        salary_pct = 0.5
        social_media = 0.5
        
        # Market reach based on DMA ranking
        market_reach = self._get_market_reach_factor(new_team_data.dma_ranking)
        
        return self.tv_rating_estimator.estimate_impact(
            scoring_percentile=scoring_pct,
            salary_percentile=salary_pct,
            social_media_index=social_media,
            league_viewership_growth=0.15,  # Assume 15% growth in new market
            market_reach_factor=market_reach
        )
    
    def _estimate_new_city_ticket_premium(
        self,
        player_data: PlayerData,
        new_team_data: TeamData,
        league_data: LeagueData
    ) -> float:
        """Estimate ticket premium in new city"""
        latest_team_record = new_team_data.annual_records[-1]
        
        # Use team's actual attendance if available
        base_attendance = latest_team_record.attendance_avg if latest_team_record.attendance_avg > 0 else 9000
        
        # Estimate attendance increase (10-50% based on player impact)
        attendance_increase_pct = 0.3  # 30% increase assumption
        new_attendance = base_attendance * (1 + attendance_increase_pct)
        
        return self.ticket_premium_estimator.estimate_premium(
            attendance_with_player=new_attendance,
            attendance_without_player=base_attendance,
            avg_ticket_price=50,
            player_performance_weight=0.35,
            star_power_multiplier=1.2,
            home_games=20
        )
    
    def _get_league_record(self, league_data: LeagueData, year: int):
        """Get league record for a specific year"""
        for record in league_data.annual_records:
            if record.year == year:
                return record
        return None
    
    def _get_market_tier_factor(self, market_tier: int) -> float:
        """Get market tier adjustment factor"""
        tier_factors = {1: 1.25, 2: 1.0, 3: 0.85}
        return tier_factors.get(market_tier, 1.0)
    
    def _get_market_reach_factor(self, dma_ranking: int) -> float:
        """Get market reach factor based on DMA ranking"""
        # Top 10 markets: 1.3-1.5
        # Mid markets (11-50): 1.0-1.3
        # Smaller markets (51+): 0.5-1.0
        if dma_ranking <= 10:
            return 1.4
        elif dma_ranking <= 50:
            return 1.2
        else:
            return 0.8
