"""Player revenue attribution calculator for team revenue impact"""


class PlayerRevenueAttributor:
    """
    Calculate player's attributed share of team revenue change
    
    Formula: Player Revenue Impact = (Team Revenue Change) × (Performance Weight) × (Playing Time %)
    Performance Weight = (Player PPG / Team PPG) × 0.6 + (Player Salary / Team Cap) × 0.4
    Playing Time % = (Games Played / Total Games) × (Minutes Per Game / 40)
    
    This estimates how much of a team's revenue change can be attributed to a specific player.
    """
    
    def calculate_attribution(
        self,
        team_revenue_change: float,
        player_ppg: float,
        team_ppg: float,
        player_salary: float,
        team_salary_cap: float,
        games_played: int,
        total_games: int,
        minutes_per_game: float
    ) -> float:
        """
        Calculate player's attributed share of team revenue change
        
        Args:
            team_revenue_change: Year-over-year revenue change
            player_ppg: Player points per game
            team_ppg: Team points per game
            player_salary: Player's annual salary
            team_salary_cap: Team's total salary cap
            games_played: Games player participated in
            total_games: Total games in season
            minutes_per_game: Player's average minutes per game
            
        Returns:
            Player's attributed revenue impact
            
        Raises:
            ValueError: If input values are invalid
            
        Example:
            >>> attributor = PlayerRevenueAttributor()
            >>> # Caitlin Clark: $22.9M revenue increase, 19.2 PPG / 84.5 team PPG
            >>> # $76K salary / $1.46M cap, 40/40 games, 35 MPG
            >>> impact = attributor.calculate_attribution(22_900_000, 19.2, 84.5, 76_000, 1_460_000, 40, 40, 35)
            >>> # Performance weight: (19.2/84.5)×0.6 + (76K/1.46M)×0.4 = 0.157
            >>> # Playing time: (40/40) × (35/40) = 0.875
            >>> # Impact: $22.9M × 0.157 × 0.875 = $3.14M
        """
        # Validate inputs
        if team_ppg <= 0:
            raise ValueError(f"team_ppg must be positive, got {team_ppg}")
        
        if team_salary_cap <= 0:
            raise ValueError(f"team_salary_cap must be positive, got {team_salary_cap}")
        
        if total_games <= 0:
            raise ValueError(f"total_games must be positive, got {total_games}")
        
        if player_ppg < 0:
            raise ValueError(f"player_ppg must be non-negative, got {player_ppg}")
        
        if player_salary < 0:
            raise ValueError(f"player_salary must be non-negative, got {player_salary}")
        
        if games_played < 0:
            raise ValueError(f"games_played must be non-negative, got {games_played}")
        
        if minutes_per_game < 0:
            raise ValueError(f"minutes_per_game must be non-negative, got {minutes_per_game}")
        
        if games_played > total_games:
            raise ValueError(
                f"games_played ({games_played}) cannot exceed total_games ({total_games})"
            )
        
        if minutes_per_game > 40:
            raise ValueError(
                f"minutes_per_game ({minutes_per_game}) cannot exceed 40 (regulation game length)"
            )
        
        # Calculate performance weight
        scoring_contribution = (player_ppg / team_ppg) * 0.6
        salary_contribution = (player_salary / team_salary_cap) * 0.4
        performance_weight = scoring_contribution + salary_contribution
        
        # Calculate playing time percentage
        games_percentage = games_played / total_games
        minutes_percentage = minutes_per_game / 40
        playing_time_pct = games_percentage * minutes_percentage
        
        # Calculate attributed revenue impact
        attributed_impact = team_revenue_change * performance_weight * playing_time_pct
        
        return attributed_impact
