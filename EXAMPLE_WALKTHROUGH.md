# Example Script Walkthrough: example.py

## Overview

The `example.py` script demonstrates how to use the Brand Portability Formula calculator to analyze a real-world WNBA player trade scenario. It uses **Maya Vance's move from Indiana Fever to Golden State Valkyries** as a case study, showing the complete workflow from data loading to result interpretation.

## What Does This Script Do?

The script calculates the **Brand Portability Score (χ)** for Maya Vance joining the Golden State Valkyries, which measures her potential impact on team value and revenue. The calculation uses the formula:

**χ = Ch ⋅ Ma / (ΔRm + ΔVt)**

Where:
- **χ (Chi)**: Brand Portability Score
- **Ch**: Career Historical Baseline
- **Ma**: Market Adjustment Factor
- **ΔRm**: Revenue Delta
- **ΔVt**: Team Value Lift

## Script Structure

The script is organized into clear, reusable functions that demonstrate each step of the calculation process:

### 1. Data Loading (`load_data_from_files()`)

**Purpose:** Load team valuations and market tier data from local files.

**What it does:**
- Loads Forbes 2025 WNBA team valuations from CSV
- Loads 2024 market tier data (historical)
- Loads 2026 market tier projections

**Files used:**
- `data/Forbes top 12 most valueable wnba teams 2025.csv`
- `data/WNBA 2024 market tiers data.json`
- `data/WNBA 2026 Market Tiers.json`

**Output:** Returns the loaded data for use in calculations.

---

### 2. Player Data Creation (`create_maya_vance_data()`)

**Purpose:** Create a `PlayerData` object with Maya Vance's statistics.

**Data included:**
- **Player ID:** `vance_maya`
- **Name:** Maya Vance
- **2025 Season Stats:**
  - 8.5 points per game (PPG)
  - 35 games played
  - 22.0 minutes per game
  - $85,000 salary
  - 65th percentile scorer (mid-tier in WNBA)

**Why this matters:** The player's performance metrics are used to calculate their career baseline (Ch) and estimate their revenue impact.

---

### 3. Team Data Creation (`create_golden_state_data()`)

**Purpose:** Create a `TeamData` object for the Golden State Valkyries with expansion team data.

**Data included:**
- **Team ID:** `golden_state_valkyries`
- **Market Tier:** 1 (Large market - San Francisco Bay Area)
- **DMA Ranking:** 6 (San Francisco-Oakland-San Jose)
- **2025 Data (Expansion baseline):**
  - Valuation: $85 million
  - Revenue: $12 million
  - Attendance: 7,500 per game
- **2026 Data (With Maya Vance):**
  - Valuation: $120 million (+41% increase)
  - Revenue: $18 million
  - Attendance: 9,500 per game

**Why this matters:** Golden State is a Tier 1 market (large market) with a high market adjustment factor (1.25), which significantly impacts the brand portability calculation. The team's growth trajectory shows the potential impact of adding a quality player to an expansion franchise.

---

### 4. League Data Creation (`create_league_data()`)

**Purpose:** Create a `LeagueData` object with WNBA league-wide statistics.

**Data included:**
- **Year:** 2026
- **Average viewership:** 1.5 million
- **Average attendance:** 8,500 per game
- **Average salary:** $120,000
- **Total teams:** 13 (includes Golden State expansion)

**Why this matters:** League averages are used to calculate the Team Value Lift (ΔVt) by comparing team growth to league-wide growth.

---

### 5. Brand Portability Calculation (`calculate_brand_portability()`)

**Purpose:** Orchestrate all calculators to compute the final Brand Portability Score.

**Process:**

1. **Initialize Estimators:**
   - `MerchandiseEstimator`: Estimates merchandise sales impact
   - `TVRatingEstimator`: Estimates TV viewership impact
   - `TicketPremiumEstimator`: Estimates ticket sales premium
   - `PlayerRevenueAttributor`: Attributes revenue to player performance

2. **Initialize Calculators:**
   - `RevenueDeltaCalculator`: Calculates ΔRm (revenue change)
   - `TeamValueLiftCalculator`: Calculates ΔVt (team value growth)
   - `CareerBaselineCalculator`: Calculates Ch (career baseline)
   - `MarketAdjustmentCalculator`: Calculates Ma (market factor)

3. **Calculate Portability:**
   - Calls `BrandPortabilityCalculator.calculate_portability()`
   - Passes all data models and parameters
   - Returns a `BrandPortabilityResult` with the χ score and component breakdown

**Parameters:**
- `player_contribution_weight`: 0.30 (30% attribution to player)
- `prior_year`: 2025
- `current_year`: 2026

---

### 6. Results Display (`display_results()`)

**Purpose:** Format and display the calculation results in human-readable format.

**What it does:**
- Uses `ResultFormatter` to convert results to readable text
- Displays the Brand Portability Score (χ)
- Shows breakdown of all components (Ch, Ma, ΔRm, ΔVt)
- Provides interpretation of the score
- Saves JSON output to `example_output.json`

**Output includes:**
- Brand Portability Score
- Career Historical Baseline breakdown
- Market Adjustment Factor details
- Revenue Delta components (merchandise, TV, tickets)
- Team Value Lift analysis
- Interpretation and warnings (if any)

---

## Running the Example

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure data files exist:**
   - `data/Forbes top 12 most valueable wnba teams 2025.csv`
   - `data/WNBA 2024 market tiers data.json`
   - `data/WNBA 2026 Market Tiers.json`

### Execute the script:

```bash
python example.py
```

### Expected Output

The script will display:

1. **Data Loading Progress:**
   ```
   Loading data from files...
   ✓ Loaded 12 team records from Forbes data
   ✓ Loaded market tier data for 2024 and 2026
   ```

2. **Player Data Summary:**
   ```
   Creating player data for Maya Vance...
   ✓ Created player data: Maya Vance
     - 8.5 PPG
     - 35 games played
     - $85,000 salary
   ```

3. **Team Data Summary:**
   ```
   Creating team data for Golden State Valkyries...
   ✓ Created team data: Golden State Valkyries
     - Market Tier: 1 (Large market)
     - DMA Ranking: 6
     - 2025 Valuation: $85,000,000
     - 2026 Valuation: $120,000,000 (+41%)
   ```

4. **Calculation Results:**
   ```
   ================================================================================
   BRAND PORTABILITY ANALYSIS
   ================================================================================
   
   Brand Portability Score (χ): [calculated value]
   Formula: χ = Ch ⋅ Ma / (ΔRm + ΔVt)
   
   INTERPRETATION:
     [Interpretation based on score]
   
   [Component breakdown follows]
   ```

5. **JSON Output:**
   - Results saved to `example_output.json`

---

## Understanding the Results

### Brand Portability Score (χ)

The χ value quantifies the player's impact:

| Score Range | Classification | Meaning |
|-------------|----------------|---------|
| **χ > 3.0** | Exceptional | Massive market impact expected |
| **2.0 < χ ≤ 3.0** | High | Significant positive effect |
| **1.0 < χ ≤ 2.0** | Moderate | Average impact |
| **0.5 < χ ≤ 1.0** | Low | Limited impact |
| **χ ≤ 0.5** | Minimal | Negligible impact |

### Component Breakdown

**Career Historical Baseline (Ch):**
- Player's average annual commercial output
- Based on career performance and revenue attribution
- Acts as the control variable

**Market Adjustment Factor (Ma):**
- Adjusts for market size and player contribution
- Tier 1 markets have a base factor of 1.25 (large markets like San Francisco)
- Modified by DMA ranking and player contribution weight

**Revenue Delta (ΔRm):**
- Change in player-specific revenue in new market
- Components:
  - Merchandise sales estimate
  - TV rating impact estimate
  - Ticket premium estimate

**Team Value Lift (ΔVt):**
- Team's growth rate minus league average
- Golden State Valkyries: Expansion team growth trajectory
- Shows team-specific value increase

---

## Customizing the Example

### Using Different Players

Modify `create_maya_vance_data()` to use different player stats:

```python
annual_record = PlayerAnnualRecord(
    year=2026,
    team_id="your_team_id",
    points_per_game=15.5,  # Your player's PPG
    games_played=38,
    minutes_per_game=28.0,
    salary=95000.0,
    scoring_percentile=0.75  # Adjust based on league ranking
)
```

### Using Different Teams

Modify `create_golden_state_data()` to analyze different teams:

```python
team_data = TeamData(
    team_id="your_team_id",
    team_name="Your Team Name",
    market_tier=2,  # 1, 2, or 3
    dma_ranking=15,  # Your market's DMA ranking
    annual_records=[...]  # Your team's valuation history
)
```

### Adjusting Parameters

Modify calculation parameters in `calculate_brand_portability()`:

```python
result = calculator.calculate_portability(
    player_contribution_weight=0.35,  # Increase player attribution
    prior_year=2024,  # Change comparison years
    current_year=2025,
    # ... other parameters
)
```

---

## Key Takeaways

1. **Modular Design:** Each function handles a specific part of the workflow, making it easy to understand and modify.

2. **Real Data:** Uses actual 2024-2025 WNBA data, demonstrating the formula's practical application.

3. **Complete Workflow:** Shows the entire process from data loading to result interpretation.

4. **Reusable Code:** Functions can be adapted for different players, teams, and scenarios.

5. **Transparent Results:** Provides full breakdown of all calculations, not just the final score.

---

## Next Steps

After understanding this example, you can:

1. **Modify the script** to analyze different player-team combinations
2. **Use the CLI** for quick calculations without writing code
3. **Integrate the API** into your own applications
4. **Explore the test suite** to see property-based testing in action
5. **Read the design document** for deeper understanding of the architecture

For more information, see:
- [README.md](README.md) - Full documentation
- [GLOSSARY.md](GLOSSARY.md) - Technical term definitions
- [requirements.md](.kiro/specs/brand-portability-formula/requirements.md) - Detailed requirements
- [design.md](.kiro/specs/brand-portability-formula/design.md) - System architecture

---

## Troubleshooting

### Common Issues

**"File not found" errors:**
- Ensure data files are in the `data/` directory
- Check file paths match exactly (case-sensitive on Linux/Mac)

**Import errors:**
- Run `pip install -r requirements.txt`
- Ensure you're in the project root directory

**Calculation errors:**
- Check that all data values are positive numbers
- Ensure years are in correct chronological order
- Verify market tier is 1, 2, or 3

**Unexpected results:**
- Review input data for accuracy
- Check that player contribution weight is between 0.0 and 1.0
- Verify team valuation data is realistic

---

**Project:** ETM-527-001 | Winter 2026 | Portland State University
