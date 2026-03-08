"""Result formatter for brand portability calculations"""
import json
from typing import Dict, Any

from src.calculators.brand_portability_calculator import BrandPortabilityResult


class ResultFormatter:
    """
    Format brand portability results in various output formats
    
    Provides methods to serialize BrandPortabilityResult to:
    - JSON string for API responses
    - Dictionary for programmatic access
    - Human-readable text for reports
    - Interpretation based on chi value ranges
    """
    
    def to_json(self, result: BrandPortabilityResult) -> str:
        """
        Serialize result to JSON string
        
        Args:
            result: BrandPortabilityResult to serialize
            
        Returns:
            JSON string representation of the result
        """
        result_dict = self.to_dict(result)
        return json.dumps(result_dict, indent=2)
    
    def to_dict(self, result: BrandPortabilityResult) -> Dict[str, Any]:
        """
        Convert result to dictionary
        
        Args:
            result: BrandPortabilityResult to convert
            
        Returns:
            Dictionary representation of the result
        """
        return {
            "brandPortability": result.chi,
            "components": {
                "careerBaseline": {
                    "avgAnnualOutput": result.components.career_baseline.avg_annual_output,
                    "totalYears": result.components.career_baseline.total_years,
                    "annualBreakdown": [list(item) for item in result.components.career_baseline.annual_breakdown]
                },
                "marketAdjustment": {
                    "adjustmentFactor": result.components.market_adjustment.adjustment_factor,
                    "baseTierFactor": result.components.market_adjustment.base_tier_factor,
                    "dmaAdjustment": result.components.market_adjustment.dma_adjustment,
                    "playerContributionWeight": result.components.market_adjustment.player_contribution_weight
                },
                "revenueDelta": {
                    "totalDelta": result.components.revenue_delta.total_delta,
                    "careerAvgRevenue": result.components.revenue_delta.career_avg_revenue,
                    "newCityRevenue": result.components.revenue_delta.new_city_revenue,
                    "components": result.components.revenue_delta.components
                },
                "teamValueLift": {
                    "netLift": result.components.team_value_lift.net_lift,
                    "teamGrowthRate": result.components.team_value_lift.team_growth_rate,
                    "leagueAvgGrowthRate": result.components.team_value_lift.league_avg_growth_rate,
                    "teamValuationPrior": result.components.team_value_lift.team_valuation_prior,
                    "teamValuationCurrent": result.components.team_value_lift.team_valuation_current
                }
            },
            "formula": result.formula,
            "interpretation": result.interpretation,
            "warnings": result.warnings
        }
    
    def to_readable_text(self, result: BrandPortabilityResult) -> str:
        """
        Format result as human-readable text
        
        Args:
            result: BrandPortabilityResult to format
            
        Returns:
            Human-readable text representation
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("BRAND PORTABILITY ANALYSIS")
        lines.append("=" * 80)
        lines.append("")
        
        # Main result
        lines.append(f"Brand Portability Score (χ): {result.chi:.2f}")
        lines.append(f"Formula: {result.formula}")
        lines.append("")
        
        # Interpretation
        lines.append("INTERPRETATION:")
        lines.append(f"  {result.interpretation}")
        lines.append("")
        
        # Warnings
        if result.warnings:
            lines.append("WARNINGS:")
            for warning in result.warnings:
                lines.append(f"  ⚠ {warning}")
            lines.append("")
        
        # Component breakdown
        lines.append("-" * 80)
        lines.append("COMPONENT BREAKDOWN")
        lines.append("-" * 80)
        lines.append("")
        
        # Career Baseline (Ch)
        cb = result.components.career_baseline
        lines.append(f"Career Historical Baseline (Ch): ${cb.avg_annual_output:,.2f}")
        lines.append(f"  Total Years: {cb.total_years}")
        lines.append("  Annual Breakdown:")
        for year, output in cb.annual_breakdown:
            lines.append(f"    {year}: ${output:,.2f}")
        lines.append("")
        
        # Market Adjustment (Ma)
        ma = result.components.market_adjustment
        lines.append(f"Market Adjustment Factor (Ma): {ma.adjustment_factor:.3f}")
        lines.append(f"  Base Tier Factor: {ma.base_tier_factor:.3f}")
        lines.append(f"  DMA Adjustment: {ma.dma_adjustment:.3f}")
        lines.append(f"  Player Contribution Weight: {ma.player_contribution_weight:.3f}")
        lines.append("")
        
        # Revenue Delta (ΔRm)
        rd = result.components.revenue_delta
        lines.append(f"Revenue Delta (ΔRm): ${rd.total_delta:,.2f}")
        lines.append(f"  Career Average Revenue: ${rd.career_avg_revenue:,.2f}")
        lines.append(f"  New City Revenue: ${rd.new_city_revenue:,.2f}")
        lines.append("  Component Breakdown:")
        lines.append(f"    Merchandise: ${rd.components['merchandise']:,.2f}")
        lines.append(f"    TV Rating: ${rd.components['tv_rating']:,.2f}")
        lines.append(f"    Ticket Premium: ${rd.components['ticket_premium']:,.2f}")
        lines.append("")
        
        # Team Value Lift (ΔVt)
        tvl = result.components.team_value_lift
        lines.append(f"Team Value Lift (ΔVt): {tvl.net_lift:.2%}")
        lines.append(f"  Team Growth Rate: {tvl.team_growth_rate:.2%}")
        lines.append(f"  League Avg Growth Rate: {tvl.league_avg_growth_rate:.2%}")
        lines.append(f"  Team Valuation (Prior): ${tvl.team_valuation_prior:,.2f}")
        lines.append(f"  Team Valuation (Current): ${tvl.team_valuation_current:,.2f}")
        lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_interpretation(self, chi: float) -> str:
        """
        Generate interpretation based on chi value
        
        Ranges:
        - χ > 3.0: Exceptional portability - star player with massive market impact
        - 2.0 < χ ≤ 3.0: High portability - significant impact expected
        - 1.0 < χ ≤ 2.0: Moderate portability - average impact
        - 0.5 < χ ≤ 1.0: Low portability - limited impact
        - χ ≤ 0.5: Minimal portability - negligible impact
        
        Args:
            chi: Brand portability score
            
        Returns:
            Human-readable interpretation string
        """
        if chi > 3.0:
            return (
                "Exceptional portability - star player with massive market impact. "
                "This player is expected to significantly boost team value and revenue "
                "in the new market."
            )
        elif chi > 2.0:
            return (
                "High portability - significant impact expected. "
                "This player should have a strong positive effect on team value and revenue."
            )
        elif chi > 1.0:
            return (
                "Moderate portability - average impact. "
                "This player will likely contribute positively to team value and revenue, "
                "but not dramatically."
            )
        elif chi > 0.5:
            return (
                "Low portability - limited impact. "
                "This player may have minimal effect on team value and revenue in the new market."
            )
        else:
            return (
                "Minimal portability - negligible impact. "
                "This player is unlikely to significantly affect team value or revenue."
            )
