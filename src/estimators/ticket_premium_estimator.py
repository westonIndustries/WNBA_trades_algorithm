"""Ticket premium estimator for player-specific attendance impact"""


class TicketPremiumEstimator:
    """
    Estimate player-specific ticket premium from attendance increases
    
    Formula: Ticket Premium = (Attendance Diff) × (Avg Ticket Price) × (Attribution Factor) × (Home Games)
    Attribution Factor = (Player Performance Weight) × (Star Power Multiplier)
    
    This estimates the additional ticket revenue attributable to a specific player's presence.
    """
    
    def estimate_premium(
        self,
        attendance_with_player: float,
        attendance_without_player: float,
        avg_ticket_price: float,
        player_performance_weight: float,
        star_power_multiplier: float,
        home_games: int
    ) -> float:
        """
        Estimate player-specific ticket premium
        
        Args:
            attendance_with_player: Average attendance with player on roster
            attendance_without_player: Average attendance without player
            avg_ticket_price: Average ticket price for team
            player_performance_weight: Player's contribution weight (0.0 to 1.0)
            star_power_multiplier: Star power adjustment (0.5 to 2.0)
            home_games: Number of home games per season
            
        Returns:
            Estimated annual ticket premium attributable to player
            
        Raises:
            ValueError: If input values are out of valid ranges
            
        Example:
            >>> estimator = TicketPremiumEstimator()
            >>> # Caitlin Clark impact: 17K vs 9K attendance, $50 tickets, 35% attribution, 1.5x star power, 20 games
            >>> premium = estimator.estimate_premium(17000, 9000, 50, 0.35, 1.5, 20)
            >>> # Attendance diff: 8,000
            >>> # Attribution: 0.35 × 1.5 = 0.525
            >>> # Premium: 8,000 × $50 × 0.525 × 20 = $4,200,000
        """
        # Validate input ranges
        if attendance_with_player < 0:
            raise ValueError(
                f"attendance_with_player must be non-negative, got {attendance_with_player}"
            )
        
        if attendance_without_player < 0:
            raise ValueError(
                f"attendance_without_player must be non-negative, got {attendance_without_player}"
            )
        
        if avg_ticket_price <= 0:
            raise ValueError(
                f"avg_ticket_price must be positive, got {avg_ticket_price}"
            )
        
        if not 0.0 <= player_performance_weight <= 1.0:
            raise ValueError(
                f"player_performance_weight must be between 0.0 and 1.0, got {player_performance_weight}"
            )
        
        if not 0.5 <= star_power_multiplier <= 2.0:
            raise ValueError(
                f"star_power_multiplier must be between 0.5 and 2.0, got {star_power_multiplier}"
            )
        
        if home_games <= 0:
            raise ValueError(
                f"home_games must be positive, got {home_games}"
            )
        
        # Calculate attendance differential
        attendance_diff = attendance_with_player - attendance_without_player
        
        # Calculate attribution factor
        attribution_factor = player_performance_weight * star_power_multiplier
        
        # Calculate ticket premium
        ticket_premium = (
            attendance_diff *
            avg_ticket_price *
            attribution_factor *
            home_games
        )
        
        return ticket_premium
