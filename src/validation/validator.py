"""
Validation and quality assurance methods for Brand Portability Formula calculations.

This module provides cross-validation methods to ensure estimation accuracy and consistency.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import statistics


@dataclass
class ValidationResult:
    """Result of a validation check"""
    passed: bool
    metric_value: float
    threshold: float
    message: str
    details: Optional[Dict] = None


@dataclass
class OutlierResult:
    """Result of outlier detection"""
    is_outlier: bool
    value: float
    mean: float
    std_dev: float
    z_score: float
    message: str


class BrandPortabilityValidator:
    """
    Validator for Brand Portability Formula calculations.
    
    Provides methods to cross-validate estimates against actual data and
    ensure consistency across calculations.
    """
    
    def __init__(self):
        """Initialize the validator with default thresholds"""
        self.attendance_correlation_threshold = 0.7
        self.revenue_multiple_min = 2.0
        self.revenue_multiple_max = 4.0
        self.outlier_z_score_threshold = 2.0
        self.consistency_tolerance = 0.15  # ±15%
    
    def attendance_correlation_analysis(
        self,
        estimated_ticket_premiums: List[float],
        actual_attendance_changes: List[float]
    ) -> ValidationResult:
        """
        Compare estimated ticket premiums with actual attendance data.
        
        Calculates Pearson correlation coefficient between estimates and actuals.
        Target: r > 0.7 indicates strong correlation.
        
        Args:
            estimated_ticket_premiums: List of estimated ticket premium values
            actual_attendance_changes: List of actual attendance change values
            
        Returns:
            ValidationResult with correlation coefficient and pass/fail status
            
        Raises:
            ValueError: If lists are empty or have different lengths
        """
        if not estimated_ticket_premiums or not actual_attendance_changes:
            raise ValueError("Input lists cannot be empty")
        
        if len(estimated_ticket_premiums) != len(actual_attendance_changes):
            raise ValueError("Input lists must have the same length")
        
        # Calculate Pearson correlation coefficient
        correlation = self._calculate_correlation(
            estimated_ticket_premiums,
            actual_attendance_changes
        )
        
        passed = correlation >= self.attendance_correlation_threshold
        
        message = (
            f"Attendance correlation: {correlation:.3f} "
            f"({'PASS' if passed else 'FAIL'} - threshold: {self.attendance_correlation_threshold})"
        )
        
        return ValidationResult(
            passed=passed,
            metric_value=correlation,
            threshold=self.attendance_correlation_threshold,
            message=message,
            details={
                "n_samples": len(estimated_ticket_premiums),
                "estimated_mean": statistics.mean(estimated_ticket_premiums),
                "actual_mean": statistics.mean(actual_attendance_changes)
            }
        )
    
    def valuation_jump_analysis(
        self,
        player_chi_values: Dict[str, float],
        team_valuation_changes: Dict[str, float]
    ) -> ValidationResult:
        """
        Validate that star player additions correlate with larger valuation increases.
        
        Teams with high χ players should show larger valuation jumps.
        Calculates correlation between χ values and valuation changes.
        
        Args:
            player_chi_values: Dict mapping player_id to χ value
            team_valuation_changes: Dict mapping player_id to team valuation % change
            
        Returns:
            ValidationResult with correlation and pass/fail status
            
        Raises:
            ValueError: If dicts are empty or have mismatched keys
        """
        if not player_chi_values or not team_valuation_changes:
            raise ValueError("Input dictionaries cannot be empty")
        
        # Ensure we have matching keys
        common_keys = set(player_chi_values.keys()) & set(team_valuation_changes.keys())
        if not common_keys:
            raise ValueError("No matching player IDs between inputs")
        
        chi_values = [player_chi_values[k] for k in common_keys]
        valuation_changes = [team_valuation_changes[k] for k in common_keys]
        
        # Calculate correlation
        correlation = self._calculate_correlation(chi_values, valuation_changes)
        
        # Expect positive correlation (higher χ → larger valuation jump)
        passed = correlation > 0.5  # Moderate positive correlation threshold
        
        message = (
            f"Valuation jump correlation: {correlation:.3f} "
            f"({'PASS' if passed else 'FAIL'} - expected positive correlation > 0.5)"
        )
        
        return ValidationResult(
            passed=passed,
            metric_value=correlation,
            threshold=0.5,
            message=message,
            details={
                "n_players": len(common_keys),
                "avg_chi": statistics.mean(chi_values),
                "avg_valuation_change": statistics.mean(valuation_changes)
            }
        )
    
    def revenue_multiple_consistency(
        self,
        team_revenues: List[float],
        team_valuations: List[float]
    ) -> ValidationResult:
        """
        Check if revenue/valuation ratios are within industry standards.
        
        Industry standard for sports franchises: 2-4x revenue multiple.
        Calculates valuation/revenue ratio for each team and checks consistency.
        
        Args:
            team_revenues: List of team annual revenues
            team_valuations: List of team valuations
            
        Returns:
            ValidationResult with average multiple and pass/fail status
            
        Raises:
            ValueError: If lists are empty, have different lengths, or contain zeros
        """
        if not team_revenues or not team_valuations:
            raise ValueError("Input lists cannot be empty")
        
        if len(team_revenues) != len(team_valuations):
            raise ValueError("Input lists must have the same length")
        
        if any(r <= 0 for r in team_revenues):
            raise ValueError("Team revenues must be positive")
        
        # Calculate revenue multiples (valuation / revenue)
        multiples = [v / r for v, r in zip(team_valuations, team_revenues)]
        avg_multiple = statistics.mean(multiples)
        
        # Check if average is within industry standard range
        passed = self.revenue_multiple_min <= avg_multiple <= self.revenue_multiple_max
        
        message = (
            f"Revenue multiple: {avg_multiple:.2f}x "
            f"({'PASS' if passed else 'FAIL'} - expected range: "
            f"{self.revenue_multiple_min}-{self.revenue_multiple_max}x)"
        )
        
        return ValidationResult(
            passed=passed,
            metric_value=avg_multiple,
            threshold=self.revenue_multiple_max,
            message=message,
            details={
                "n_teams": len(team_revenues),
                "min_multiple": min(multiples),
                "max_multiple": max(multiples),
                "std_dev": statistics.stdev(multiples) if len(multiples) > 1 else 0.0
            }
        )
    
    def market_tier_consistency(
        self,
        tier1_impacts: List[float],
        tier2_impacts: List[float],
        tier3_impacts: List[float]
    ) -> ValidationResult:
        """
        Validate that market tier adjustments produce reasonable results.
        
        Tier 1 markets should show higher absolute impacts.
        After adjustment, relative impacts should be similar across tiers.
        
        Args:
            tier1_impacts: List of χ values for Tier 1 market players
            tier2_impacts: List of χ values for Tier 2 market players
            tier3_impacts: List of χ values for Tier 3 market players
            
        Returns:
            ValidationResult with tier consistency metrics
            
        Raises:
            ValueError: If any list is empty
        """
        if not tier1_impacts or not tier2_impacts or not tier3_impacts:
            raise ValueError("All tier impact lists must be non-empty")
        
        # Calculate means for each tier
        tier1_mean = statistics.mean(tier1_impacts)
        tier2_mean = statistics.mean(tier2_impacts)
        tier3_mean = statistics.mean(tier3_impacts)
        
        # Tier 1 should have highest mean (or at least not lowest)
        # After market adjustment, they should be reasonably close
        tier_means = [tier1_mean, tier2_mean, tier3_mean]
        overall_mean = statistics.mean(tier_means)
        
        # Check if tier means are within ±30% of overall mean
        # (more lenient than player consistency since market effects vary)
        max_deviation = max(abs(tm - overall_mean) / overall_mean for tm in tier_means)
        
        passed = max_deviation <= 0.30  # ±30% tolerance
        
        message = (
            f"Market tier consistency: max deviation {max_deviation:.1%} "
            f"({'PASS' if passed else 'FAIL'} - threshold: ±30%)"
        )
        
        return ValidationResult(
            passed=passed,
            metric_value=max_deviation,
            threshold=0.30,
            message=message,
            details={
                "tier1_mean": tier1_mean,
                "tier2_mean": tier2_mean,
                "tier3_mean": tier3_mean,
                "overall_mean": overall_mean,
                "tier1_count": len(tier1_impacts),
                "tier2_count": len(tier2_impacts),
                "tier3_count": len(tier3_impacts)
            }
        )
    
    def peer_comparison(
        self,
        player_chi_values: Dict[str, float],
        player_peer_groups: Dict[str, str]
    ) -> List[OutlierResult]:
        """
        Compare similar players to validate consistency and flag outliers.
        
        Groups players by peer group and identifies outliers
        (χ values > 2 standard deviations from peer mean).
        
        Args:
            player_chi_values: Dict mapping player_id to χ value
            player_peer_groups: Dict mapping player_id to peer_group_id
            
        Returns:
            List of OutlierResult for each player, flagging outliers
            
        Raises:
            ValueError: If dicts are empty or have mismatched keys
        """
        if not player_chi_values or not player_peer_groups:
            raise ValueError("Input dictionaries cannot be empty")
        
        # Ensure matching keys
        common_keys = set(player_chi_values.keys()) & set(player_peer_groups.keys())
        if not common_keys:
            raise ValueError("No matching player IDs between inputs")
        
        # Group players by peer group
        peer_groups: Dict[str, List[Tuple[str, float]]] = {}
        for player_id in common_keys:
            group = player_peer_groups[player_id]
            chi = player_chi_values[player_id]
            if group not in peer_groups:
                peer_groups[group] = []
            peer_groups[group].append((player_id, chi))
        
        # Analyze each peer group
        results = []
        for group_id, players in peer_groups.items():
            if len(players) < 2:
                # Can't calculate outliers with < 2 players
                for player_id, chi in players:
                    results.append(OutlierResult(
                        is_outlier=False,
                        value=chi,
                        mean=chi,
                        std_dev=0.0,
                        z_score=0.0,
                        message=f"Player {player_id}: insufficient peer group size for comparison"
                    ))
                continue
            
            chi_values = [chi for _, chi in players]
            mean = statistics.mean(chi_values)
            std_dev = statistics.stdev(chi_values) if len(chi_values) > 1 else 0.0
            
            for player_id, chi in players:
                # Calculate z-score
                z_score = (chi - mean) / std_dev if std_dev > 0 else 0.0
                is_outlier = abs(z_score) > self.outlier_z_score_threshold
                
                message = (
                    f"Player {player_id} (group {group_id}): χ={chi:.2f}, "
                    f"z-score={z_score:.2f} "
                    f"({'OUTLIER' if is_outlier else 'normal'})"
                )
                
                results.append(OutlierResult(
                    is_outlier=is_outlier,
                    value=chi,
                    mean=mean,
                    std_dev=std_dev,
                    z_score=z_score,
                    message=message
                ))
        
        return results
    
    def _calculate_correlation(
        self,
        x: List[float],
        y: List[float]
    ) -> float:
        """
        Calculate Pearson correlation coefficient between two lists.
        
        Args:
            x: First list of values
            y: Second list of values
            
        Returns:
            Correlation coefficient (-1 to 1)
        """
        if len(x) != len(y) or len(x) == 0:
            raise ValueError("Lists must be non-empty and have equal length")
        
        n = len(x)
        
        # Calculate means
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        # Calculate correlation
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        
        sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(n))
        
        denominator = (sum_sq_x * sum_sq_y) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
