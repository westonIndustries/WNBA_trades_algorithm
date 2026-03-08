# Brand Portability Formula - Requirements

## Overview
Develop an algorithm to calculate the Brand Portability Formula (χ), which measures a player's potential impact on team value and revenue when traded to a new market.

## Formula
χ = Ch ⋅ Ma / (ΔRm + ΔVt)

Where:
- χ (Brand Portability) = Higher values indicate greater potential impact on team value/revenue
- Ch = Career Historical Baseline (control variable)
- Ma = Market Adjustment Factor
- ΔRm = Revenue Delta (new city vs career average)
- ΔVt = Team Value Lift (team growth minus league average)

## User Stories

1. **As a sports analyst**, I want to calculate brand portability to evaluate a player's trade potential and understand which markets would be the best fit.

2. **As a team executive**, I want to understand the projected revenue impact before making trade decisions to maximize team value.

3. **As a data scientist**, I want modular code that allows me to test different market scenarios and adjust variables independently.

4. **As a fan or researcher**, I want interpretable results that explain how each factor contributes to the final score.

## Variable Definitions

### 1. ΔRm (Revenue Delta)
The change in player-specific revenue in the new city compared to their career average.

**Components:**
- Merchandise sales changes in new market vs career average
- Individual TV ratings spikes in new market (estimated)
- "Star-power" ticket premiums in new market (estimated)

**Requirements:**
- Calculate career average revenue metrics
- Measure new city-specific revenue impact
- Compute the delta between new city and career average
- Estimate TV rating impacts using player performance metrics, social media engagement, and league-wide viewership trends
- Estimate ticket premiums using attendance differentials, player salary as proxy, and market size adjustments

### 2. ΔVt (Team Value Lift)
The year-over-year increase in the new team's valuation or local sponsorship revenue following the trade, minus the league's average growth rate.

**Requirements:**
- Use Forbes team valuation data (2025) as baseline
- Track team revenue changes from Forbes data
- Calculate league-average growth rate from available valuation data
- Compute net lift after subtracting league average
- For historical analysis, estimate prior year valuations using revenue multiples or industry growth rates

### 3. Ch (Career Historical Baseline)
The player's average annual commercial output from their Career Data. This acts as the control variable.

**Requirements:**
- Aggregate player career data
- Calculate annual commercial output average
- Serve as control variable in formula

### 4. Ma (Market Adjustment Factor)
A weight based on Team Value data to measure actual player contribution, not just city size.

**Requirements:**
- Use market tier adjustment factors from WNBA 2026 Market Tiers data (1.25, 1.0, 0.85)
- Factor in DMA rankings for each team's market
- Adjust for team value contribution using Forbes valuation data
- Ensure fair comparison across markets (Tier 1 large markets vs Tier 3 smaller markets)

## Data Requirements

### Player Data
- Career revenue history (annual)
- Merchandise sales data (annual)
- TV rating history (annual)
- Ticket sales data (annual)

### Team Data
- Team valuation history (annual)
- Sponsorship revenue data (annual)
- Market size indicators (population, GDP, etc.)

### League Data
- Average growth rates (annual)
- Market benchmarks

### Data Format
- Input: CSV files or JSON structures
- Player data: Array of annual records per player
- Team data: Array of annual records per team
- League data: Single dataset with league-wide averages

## Data Sources

### wehoop R Package
The [wehoop package](https://wehoop.sportsdataverse.org/) provides WNBA game and player statistics:
- Play-by-play data (2002-2024) with 62 columns
- Team box scores (2003-2024) with 57 columns including assists, rebounds, field goal %, turnovers
- Player box scores (2002-2024) with individual player statistics

**Installation:**
```r
if (!requireNamespace('pacman', quietly = TRUE)){   
  install.packages('pacman') 
}  
pacman::p_load(wehoop, dplyr, glue, tictoc, progressr)
```

**Note:** wehoop provides on-court performance data but does not include financial metrics (revenue, valuations, sponsorships). This data serves as supplementary context for player performance analysis.

### WNBA Viewership Data
[Statista - WNBA Regular Season Viewers](https://www.statista.com/statistics/1236723/wnba-regular-season-viewers/) provides league-wide viewership trends from 2016-2025, useful for understanding TV ratings context and league growth patterns.

**Attribution:** Content rephrased for compliance with licensing restrictions. Data shows average viewership across media platforms in the United States for regular season games.

### WNBA Team Attendance Data
[Statista - WNBA Average Attendance by Team](https://www.statista.com/statistics/1236749/wnba-team-attendance/) provides team-specific attendance data for the 2025 season, useful for measuring "star-power" ticket premiums and market engagement.

**Attribution:** Content rephrased for compliance with licensing restrictions. Data includes average home attendance per team across the regular season, which can help identify market-specific fan engagement and potential revenue impacts from player trades.

### WNBA Player Salary Data
[Statista - Annual Salaries NBA & WNBA](https://www.statista.com/statistics/1120680/annual-salaries-nba-wnba/) provides average and minimum salary data for WNBA players in the 2024/25 season.

**Attribution:** Content rephrased for compliance with licensing restrictions. Data shows average annual pay and highest-earning player salaries in the WNBA.

**Use as Proxy:** While salaries represent team costs rather than revenue generation, they can serve as a proxy for player brand value in the Ch (Career Historical Baseline) calculation, assuming higher-paid players have stronger commercial output potential.

### WNBA Player Performance Data (Scoring Leaders)
[Statista - WNBA All-Time Scoring Leaders](https://www.statista.com/statistics/1237068/wnba-scoring-leaders/) provides career scoring totals for top WNBA players.

**Attribution:** Content rephrased for compliance with licensing restrictions. Data includes all-time points scored by individual players, useful for establishing performance baselines.

**Multi-Variable Use:**
- **Ch (Career Historical Baseline):** Career scoring averages establish historical brand strength and commercial output potential
- **ΔRm (Revenue Delta):** Scoring performance in new market vs career average helps estimate TV rating impacts and ticket premium changes
- **Ma (Market Adjustment Factor):** Scoring data helps normalize player contribution across different market sizes, ensuring fair comparison between high-scoring players in small vs large markets

### Local Data Files

**Forbes WNBA Team Valuations (2025)**
- File: `data/Forbes top 12 most valueable wnba teams 2025.csv`
- Contains: Team valuations, revenue, and ownership data for all 12 WNBA teams in 2025
- **Use for ΔVt:** Calculate team value lift using valuation and revenue data
- **Use for Ma:** Baseline valuations for market adjustment calculations

**WNBA 2024 Market Tiers (Historical Data)**
- File: `data/WNBA 2024 market tiers data.json`
- Contains: 2024 team valuations and 2023 revenue for all 12 teams
- Includes market tier classifications with adjustment factors (1.25, 1.0, 0.85)
- **Use for ΔVt:** Calculate year-over-year valuation changes (2024 → 2025)
- **Use for Ch:** Establish historical baseline using 2023 revenue data
- **Use for Ma:** Historical market tier assignments

**WNBA 2026 Market Tiers (Projection Data)**
- File: `data/WNBA 2026 Market Tiers.json`
- Contains: Market tier classifications (Tier 1, 2, 3) with adjustment factors (1.25, 1.0, 0.85)
- Includes DMA rankings and valuation estimates for 15 teams (including 2026 expansion teams)
- **Use for Ma:** Pre-calculated market adjustment factors by tier
- **Use for ΔRm:** Market size context for estimating revenue deltas

**Market Tier Definitions:**
- Tier 1 (Factor: 1.25): Large markets - NY, LA, SF, Toronto
- Tier 2 (Factor: 1.0): Mid-size markets - Seattle, Indiana, Las Vegas, Chicago, Phoenix, Portland
- Tier 3 (Factor: 0.85): Smaller markets - Dallas, Washington, Minnesota, Atlanta, Connecticut

**Data Source Documentation:**
- Files: `data/WNBA 2024 market tiers data from.txt`, `data/WNBA 2026 market tiers data from.txt`
- Contains: References to primary sources (Sportico, Forbes, Nielsen DMA, Across the Timeline)
- Provides context on data collection methodology and industry standards

### Data Completeness Status

**✅ Available Data:**
- Historical team valuations: 2024 valuations and 2023 revenue (from `data/WNBA 2024 market tiers data.json`)
- Current team valuations: 2025 valuations and revenue (from `data/Forbes top 12 most valueable wnba teams 2025.csv`)
- Market tier adjustment factors: Pre-calculated for 2024 and 2026
- Player performance data: Scoring, stats from wehoop and Statista
- League-wide trends: Viewership, attendance, salary data

**⚠️ Data to be Estimated:**
- Player-specific merchandise sales (will use estimation formulas below)
- Individual player revenue attribution (will use estimation formulas below)

### Estimation Methods Required
Since some data is not publicly available, the following will need to be estimated:

#### 1. Player-Specific Merchandise Sales Estimation

**Formula:**
```
Merchandise Sales = (Scoring Percentile × Salary Percentile × Market Tier Factor) × League Revenue Baseline
```

**Calculation Steps:**
1. Calculate player's scoring percentile within league (using wehoop/Statista scoring data)
2. Calculate player's salary percentile (using Statista salary data)
3. Apply market tier factor (1.25, 1.0, or 0.85 based on team's market tier)
4. Multiply by league revenue baseline (derived from average team revenue in Forbes data)

**Example:**
- Player scoring percentile: 0.95 (top 5% scorer)
- Salary percentile: 0.90 (top 10% earner)
- Market tier factor: 1.25 (Tier 1 market)
- League revenue baseline: $18M (average from Forbes data)
- Estimated merchandise sales: 0.95 × 0.90 × 1.25 × $18M × 0.05 = $0.96M

#### 2. Individual Player Revenue Attribution

**Formula:**
```
Player Revenue Impact = (Team Revenue Change) × (Player Performance Weight) × (Playing Time %)
```

**Calculation Steps:**
1. Calculate team revenue change: Revenue(Year N) - Revenue(Year N-1)
2. Calculate player performance weight:
   ```
   Performance Weight = (Player Points Per Game / Team Points Per Game) × 0.6 +
                        (Player Salary / Team Salary Cap) × 0.4
   ```
3. Calculate playing time percentage: (Games Played / Total Games) × (Minutes Per Game / 40)
4. Multiply all factors together

**Example (Caitlin Clark Impact on Indiana Fever):**
- Team revenue change: $32M (2025) - $9.1M (2023) = $22.9M
- Player PPG: 19.2, Team PPG: 84.5 → 19.2/84.5 = 0.227
- Player salary: $76K, Team cap: ~$1.46M → 76K/1.46M = 0.052
- Performance weight: (0.227 × 0.6) + (0.052 × 0.4) = 0.157
- Playing time: (40/40) × (35/40) = 0.875
- Player revenue impact: $22.9M × 0.157 × 0.875 = $3.14M

#### 3. Player-Specific TV Rating Impact

**Formula:**
```
TV Rating Impact = (Player Star Power Score) × (League Viewership Growth) × (Market Reach Factor)
```

**Calculation Steps:**
1. Calculate player star power score:
   ```
   Star Power = (Scoring Percentile × 0.4) + (Salary Percentile × 0.3) + (Social Media Index × 0.3)
   ```
2. Use league viewership growth from Statista data
3. Apply market reach factor based on DMA ranking
4. Estimate individual contribution to viewership spikes

**Data Sources:**
- Player performance: wehoop, Statista scoring leaders
- League viewership: Statista WNBA viewership data
- Market reach: DMA rankings from market tiers data

#### 4. Player-Specific Ticket Premium

**Formula:**
```
Ticket Premium = (Attendance Differential) × (Average Ticket Price) × (Attribution Factor)
```

**Calculation Steps:**
1. Calculate attendance differential:
   ```
   Attendance Diff = Team Attendance(with player) - Team Attendance(without player)
   ```
2. Use average ticket price from Statista or estimate from market tier
3. Calculate attribution factor:
   ```
   Attribution Factor = (Player Performance Weight) × (Star Power Multiplier)
   ```
4. Multiply to get total ticket premium attributable to player

**Example:**
- Attendance increase: 17,000 - 9,000 = 8,000 per game
- Average ticket price: $50
- Attribution factor: 0.35 (player contributes 35% of increase)
- Games per season: 20 home games
- Ticket premium: 8,000 × $50 × 0.35 × 20 = $2.8M

#### 5. League-Average Growth Rate Calculation

**Formula:**
```
League Avg Growth = Σ(Team Valuation Change) / Number of Teams / Prior Year Avg Valuation
```

**Calculation Steps:**
1. Calculate each team's valuation change from 2024 to 2025
2. Sum all changes
3. Divide by number of teams (12)
4. Divide by average 2024 valuation to get percentage growth

**Example Using Available Data:**
- 2024 average valuation: ($140M + $135M + $130M + ... + $55M) / 12 ≈ $97.5M
- 2025 average valuation: ($400M + $370M + $330M + ... + $190M) / 12 ≈ $269M
- League average growth: ($269M - $97.5M) / $97.5M = 175.9%

### Validation Methods

To ensure estimation accuracy, cross-validate using:

1. **Attendance Correlation Analysis**
   - Compare estimated ticket premiums with actual attendance data
   - Validate using before/after player arrival attendance figures

2. **Valuation Jump Analysis**
   - Teams with star player additions should show larger valuation increases
   - Example: Indiana Fever +311% (2024→2025) with Caitlin Clark vs league avg +175.9%

3. **Revenue Multiple Consistency**
   - Check if estimated player impacts align with team revenue multiples
   - Compare revenue growth to valuation growth ratios

4. **Market Tier Consistency**
   - Ensure Tier 1 markets show higher absolute impacts but similar relative impacts
   - Validate that market adjustment factors (1.25, 1.0, 0.85) produce reasonable results

5. **Peer Comparison**
   - Compare similar players in similar markets to validate consistency
   - Flag outliers for manual review

## Acceptance Criteria

1. Each variable (ΔRm, ΔVt, Ch, Ma) has its own dedicated code module
2. Formula calculates χ correctly with all variables
3. Each variable's calculation is unit tested
4. Edge cases handled (zero values, missing data)
5. Output is interpretable and documented

## Edge Cases and Error Handling

1. **Zero Career Average**: If career average revenue is zero, return error or use league average as fallback
2. **Division by Zero**: If ΔRm + ΔVt = 0, return error or apply small epsilon adjustment
3. **Missing Data**: Handle missing annual data points with interpolation or exclusion
4. **Negative Values**: Define behavior for negative revenue deltas
5. **Insufficient Data**: Require minimum years of data (e.g., 3 years minimum)

## Output Requirements

1. **Primary Output**: Single χ value representing brand portability score
2. **Intermediate Values**: Expose all component values (ΔRm, ΔVt, Ch, Ma) for transparency
3. **Format**: JSON object with structured output
4. **Documentation**: Each output field documented with calculation method

## Example Output Format

```json
{
  "brandPortability": 2.45,
  "components": {
    "careerBaseline": 5000000,
    "marketAdjustment": 1.2,
    "revenueDelta": 3000000,
    "teamValueLift": 2000000
  },
  "formula": "χ = Ch ⋅ Ma / (ΔRm + ΔVt)",
  "interpretation": "Above average portability - player likely to have significant impact in new market"
}
```
