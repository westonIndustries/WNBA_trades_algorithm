# WNBA Player Portability Model
### ETM-527-001 | Winter 2026 | Portland State University

This repository contains the methodology, architecture, and implementation requirements for analyzing WNBA player valuation and "portability" surpluses. This document serves as a conceptual and technical map for the data pipeline and model logic.

🎵 **Listen to the Algorithm:** [The Portability Formula on SoundCloud](https://soundcloud.com/orion-vale-523406667/the-portability-formula)

---

## 📊 The Portability Formula (Algorithm)

(Verse 1: Data Initialization)
Initialize the frame, set the `player_id`,  
Cross the roster history, find where the talent hid.  
We’re pulling `trade_date` timestamps, measuring the stay,  
A binary indicator: did they move or did they play?  
Extract the `team_iso`, join it by the year,  
The Portability Index is finally drawing near.

### (Verse 2: Financial Sources & Coefficients)
Scrape the logs from Spotrac, the ceiling and the floor,  
Hit Across the Timeline tables, scanning for some more.  
Pull the cap from Her Hoop Stats, every dollar, every cent,  
Verify the `base_salary` where the roster money’s spent.  
Add a dummy for the Supermax, a 1 or a 0,  
Is the contract undervalued for a franchise hero?

### (Verse 3: Social Sources & Brand Variance)
Get the STN Digital report, the engagement and the reach,  
Check Zoomph for social value and the lessons that they teach.  
Hit HypeAuditor's API for the `follower_count` base,  
Log-transform the growth to normalize the pace.  
That’s the Surplus Value, the $V$ minus the $C$,  
The hidden ROI that the scouts don't always see.

### (Chorus)
It’s a multi-factor model, weighing power and the price,  
Optimizing rosters, we don’t need to roll the dice.  
From the `engagement_rate` to the `follower_count`,  
We’re calculating surplus in a scalable amount.  
From the `rookie_scale` floor to the `supermax` peak,  
It’s the alpha in the data that the franchises seek.

### (Verse 4: Performance Weights & Metrics)
Hit Basketball-Reference for the `win_shares` and the PER,  
Scrape Official WNBA Stats for the usage in the air.  
Check the Fanatics rankings for the `jersey_sales` rank,  
That's the brand liquidity you can take straight to the bank.  
Cross-reference Attendance from the official box score,  
Does the `attendance_delta` show the fans are wanting more?

### (Bridge: Structural Break)
Account for the 2026 Shift, the `structural_break`,  
The old coefficients are a risk we shouldn't take.  
Re-calibrate the Revenue Share as a dynamic float,  
The new CBA is the rising tide for every boat.

### (Outro: The Component Breakdown)
`model.fit(X, y)`... let the coefficients speak,  
Is it `brand_equity` or usage that we seek?  
The Intercept is culture, the baseline of the play,  
The Residual is magic that the numbers can’t convey.  
The $V$ is for the Value that the social metrics bring,  
The $C$ is for the Contract, the financial tethering.  
When $V$ is more than $C$, the Portability is high,  
That’s a player you can build on, reaching for the sky.  
Check the R-squared on the brand, see the fit within the frame,  
The future of the league is in the data of the game.  
`print(portability_index)`... now the data run is through,  
Stamping the credits on the PSU floor,  
ETM-527... Winter '26, open the door!


**Research Context & Economic Variables:** [WNBA Financial Reality: Revenue, Losses, and Fair Pay](https://www.youtube.com/watch?v=1KycKWZBLX8)

---

## 📋 Model Requirements & Logic

The **WNBA Player Portability Model** centers on calculating a portability score ($\chi$) to estimate a player's commercial and financial impact when moving to a new team.

### Core Formula
The system implements the formula:
$$\chi = \frac{Ch \cdot Ma}{\Delta Rm + \Delta Vt}$$

* **$\chi$ (Brand Portability):** Higher values indicate a greater potential impact on team value and revenue.
* **$Ch$ (Career Historical Baseline):** The player's average annual commercial output acting as a control variable.
* **$Ma$ (Market Adjustment Factor):** A weight based on team value data to measure actual contribution rather than city size.
* **$\Delta Rm$ (Revenue Delta):** Projected change in player-specific revenue in the new city compared to their career average.
* **$\Delta Vt$ (Team Value Lift):** Net increase in new team valuation following the trade, minus league average growth.

For detailed definitions of all variables and technical terms, see the [Technical Glossary](GLOSSARY.md).

For a complete breakdown of user stories and estimation methods, refer to the [requirements.md](./requirements.md).

---

## 🏗️ System Architecture & Design

The system follows a modular, layered architecture to ensure separation of concerns between data ingestion, estimation, and final calculation.

### High-Level Components
1.  **Application Layer**: Handles the Formula Calculator, Result Formatter, and API interface.
2.  **Calculation Layer**: Independent modules for $\Delta Rm$, $\Delta Vt$, $Ch$, and $Ma$.
3.  **Estimation Layer**: Specialized engines for Merchandise, TV Ratings, Ticket Premiums, and Revenue Attribution.
4.  **Data Layer**: Adapters for `wehoop`, Statista, and local CSV/JSON files (e.g., Forbes Valuations).

### Design Principles
* **Modularity**: Each variable calculation is isolated to allow for independent testing and updates.
* **Transparency**: Intermediate values are exposed in the JSON output for full interpretability.
* **Error Resilience**: Graceful handling of division-by-zero (epsilon adjustments) and missing historical data.

### Primary Data Models
* **PlayerData**: Career stats, annual PPG, and salary history.
* **TeamData**: Forbes valuations, local revenue, and market tier classifications.
* **LeagueData**: Year-over-year viewership, attendance, and salary benchmarks.

Full architecture diagrams and class definitions can be found in the [design.md](./design.md).

---

## 🛠️ Project Dependencies

To run the analysis scripts associated with this model, the following environments are required:

### [cite_start]Python Requirements (`requirements.txt`) [cite: 1]
* **Core**: `pandas>=2.0.0`, `numpy>=1.24.0`
* **R Integration**: `rpy2>=3.5.0`
* **Data Validation**: `pydantic>=2.0.0`
* **Testing**: `pytest>=7.4.0`, `hypothesis>=6.82.0`

### R Dependencies
* `wehoop`: For official WNBA statistics and play-by-play data.
* `tidyverse`: For data manipulation and visualization.

---

## 🚀 Getting Started

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd brand-portability-formula
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install R and wehoop package (optional, for live data):**
```r
# In R console
if (!requireNamespace('pacman', quietly = TRUE)){   
  install.packages('pacman') 
}  
pacman::p_load(wehoop, dplyr, glue, tictoc, progressr)
```

4. **Verify data files are present:**
Ensure the following files exist in the `data/` directory:
   - `Forbes top 12 most valueable wnba teams 2025.csv`
   - `WNBA 2024 market tiers data.json`
   - `WNBA 2026 Market Tiers.json`

### Quick Start - Run Example Script

The easiest way to get started is to run the example script:

```bash
python example.py
```

This demonstrates the complete workflow using the Maya Vance from Indiana Fever to Golden State Valkyries scenario and outputs both human-readable text and JSON results.

**For a detailed walkthrough of the example script, see [EXAMPLE_WALKTHROUGH.md](EXAMPLE_WALKTHROUGH.md).**

---

## 📖 Usage Guide

### Option 1: Using the Example Script (Recommended for Learning)

The `example.py` script provides a complete, documented example of how to use the Brand Portability Formula calculator programmatically.

**Run the example:**
```bash
python example.py
```

**What it does:**
1. Loads data from CSV and JSON files
2. Creates player, team, and league data models
3. Calculates brand portability for Maya Vance → Golden State Valkyries
4. Displays results in human-readable format
5. Saves JSON output to `example_output.json`

**Customize the example:**
Edit `example.py` to change player stats, team data, or calculation parameters.

**Learn more:**
For a step-by-step explanation of how the example script works, see the [Example Walkthrough Guide](EXAMPLE_WALKTHROUGH.md).

### Option 2: Using the Command-Line Interface (CLI)

The CLI provides a quick way to calculate brand portability without writing code.

**Basic usage:**
```bash
python -m src.cli \
  --player-id <player_id> \
  --new-team-id <team_id> \
  --player-name "<Player Name>" \
  --player-ppg <points_per_game> \
  --player-salary <annual_salary> \
  --player-games <games_played> \
  --player-minutes <minutes_per_game> \
  --team-ppg <team_points_per_game>
```

**Example 1: Caitlin Clark to Indiana Fever**
```bash
python -m src.cli \
  --player-id clark_caitlin \
  --new-team-id indiana_fever \
  --player-name "Caitlin Clark" \
  --player-ppg 19.2 \
  --player-salary 76535 \
  --player-games 40 \
  --player-minutes 35.4 \
  --team-ppg 84.5
```

**Example 2: Maya Vance from Indiana Fever to Golden State**
```bash
python -m src.cli \
  --player-id vance_maya \
  --new-team-id golden_state_valkyries \
  --player-name "Maya Vance" \
  --player-ppg 8.5 \
  --player-salary 85000 \
  --player-games 35 \
  --player-minutes 22.0 \
  --team-ppg 82.3 \
  --json
```

**Get JSON output:**
Add the `--json` flag to output results in JSON format:
```bash
python -m src.cli \
  --player-id vance_maya \
  --new-team-id golden_state_valkyries \
  --player-name "Maya Vance" \
  --player-ppg 8.5 \
  --player-salary 85000 \
  --player-games 35 \
  --player-minutes 22.0 \
  --team-ppg 82.3 \
  --json
```

### Option 3: Programmatic API Usage

For integration into other applications, use the Python API directly.

**Basic example:**
```python
from src.models import PlayerData, PlayerAnnualRecord, TeamData, LeagueData, MarketTierData
from src.calculators.brand_portability_calculator import BrandPortabilityCalculator
from src.formatters.result_formatter import ResultFormatter

# Create player data
player_data = PlayerData(
    player_id="vance_maya",
    player_name="Maya Vance",
    annual_records=[
        PlayerAnnualRecord(
            year=2025,
            team_id="indiana_fever",
            points_per_game=8.5,
            games_played=35,
            minutes_per_game=22.0,
            salary=85000.0,
            scoring_percentile=0.65
        )
    ]
)

# Create team data (new team: Golden State)
team_data = TeamData(
    team_id="golden_state_valkyries",
    team_name="Golden State Valkyries",
    market_tier=1,  # Tier 1 - Large market
    dma_ranking=6,  # San Francisco Bay Area
    annual_records=[...]  # Add team annual records
)

# Initialize calculator with all dependencies
calculator = BrandPortabilityCalculator(
    revenue_delta_calc=...,
    team_value_lift_calc=...,
    career_baseline_calc=...,
    market_adjustment_calc=...
)

# Calculate portability
result = calculator.calculate_portability(
    player_data=player_data,
    new_team_data=team_data,
    league_data=league_data,
    market_tier_data=market_tier_data,
    team_data_history=[team_data],
    prior_year=2024,
    current_year=2025,
    player_contribution_weight=0.35
)

# Format results
formatter = ResultFormatter()
print(formatter.to_readable_text(result))
```

For a complete working example, see `example.py`.

---

## 📋 CLI Reference

### Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--player-id` | Player identifier (lowercase, underscore-separated) | `clark_caitlin` |
| `--new-team-id` | New team identifier (lowercase, underscore-separated) | `golden_state_valkyries` |
| `--player-name` | Player full name | `"Caitlin Clark"` |
| `--player-ppg` | Player points per game | `19.2` |
| `--player-salary` | Player annual salary (USD) | `76535` |
| `--player-games` | Games played by player | `40` |
| `--player-minutes` | Player average minutes per game | `35.4` |
| `--team-ppg` | Team points per game | `84.5` |

### Optional Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--forbes-data` | Path to Forbes valuation CSV | `data/Forbes top 12 most valueable wnba teams 2025.csv` |
| `--market-tiers-2024` | Path to 2024 market tiers JSON | `data/WNBA 2024 market tiers data.json` |
| `--market-tiers-2026` | Path to 2026 market tiers JSON | `data/WNBA 2026 Market Tiers.json` |
| `--prior-year` | Prior year for team value lift calculation | `2024` |
| `--current-year` | Current year for team value lift calculation | `2025` |
| `--json` | Output results as JSON | `false` (text output) |
| `--verbose` | Enable verbose error messages | `false` |

### Team Identifiers

Valid team IDs for the `--new-team-id` argument:

**Tier 1 Markets (Factor: 1.25):**
- `new_york_liberty`
- `los_angeles_sparks`
- `golden_state_valkyries`

**Tier 2 Markets (Factor: 1.0):**
- `seattle_storm`
- `indiana_fever`
- `las_vegas_aces`
- `chicago_sky`
- `phoenix_mercury`

**Tier 3 Markets (Factor: 0.85):**
- `dallas_wings`
- `washington_mystics`
- `minnesota_lynx`
- `atlanta_dream`
- `connecticut_sun`

---

## 📊 Understanding the Output

### Output Formats

The calculator provides two output formats:

1. **Human-Readable Text** (default): Formatted for easy reading with clear sections
2. **JSON**: Structured data for programmatic processing

### Sample Output - Text Format

```
================================================================================
BRAND PORTABILITY ANALYSIS
================================================================================

Brand Portability Score (χ): 1.45
Formula: χ = Ch ⋅ Ma / (ΔRm + ΔVt)

INTERPRETATION:
  Moderate portability - average impact. This player will likely contribute 
  positively to team value and revenue, but not dramatically.

--------------------------------------------------------------------------------
COMPONENT BREAKDOWN
--------------------------------------------------------------------------------

Career Historical Baseline (Ch): $425,000.00
  Total Years: 2
  Annual Breakdown:
    2024: $380,000.00
    2025: $470,000.00

Market Adjustment Factor (Ma): 1.18
  Base Tier Factor: 1.250 (Tier 1 - Large Market)
  DMA Adjustment: 0.945
  Player Contribution Weight: 0.350

Revenue Delta (ΔRm): $285,000.00
  Career Average Revenue: $425,000.00
  New City Revenue: $710,000.00
  Component Breakdown:
    Merchandise: $180,000.00
    TV Rating: $45,000.00
    Ticket Premium: $60,000.00

Team Value Lift (ΔVt): 62.50%
  Team Growth Rate: 75.00%
  League Avg Growth Rate: 12.50%
  Team Valuation (Prior): $120,000,000.00
  Team Valuation (Current): $210,000,000.00

================================================================================
```

### Sample Output - JSON Format

```json
{
  "brandPortability": 1.45,
  "components": {
    "careerBaseline": {
      "avgAnnualOutput": 425000.0,
      "totalYears": 2,
      "annualBreakdown": [
        [2024, 380000.0],
        [2025, 470000.0]
      ]
    },
    "marketAdjustment": {
      "adjustmentFactor": 1.18,
      "baseTierFactor": 1.25,
      "dmaAdjustment": 0.945,
      "playerContributionWeight": 0.35
    },
    "revenueDelta": {
      "totalDelta": 285000.0,
      "careerAvgRevenue": 425000.0,
      "newCityRevenue": 710000.0,
      "components": {
        "merchandise": 180000.0,
        "tv_rating": 45000.0,
        "ticket_premium": 60000.0
      }
    },
    "teamValueLift": {
      "netLift": 0.625,
      "teamGrowthRate": 0.75,
      "leagueAvgGrowthRate": 0.125,
      "teamValuationPrior": 120000000.0,
      "teamValuationCurrent": 210000000.0
    }
  },
  "formula": "χ = Ch ⋅ Ma / (ΔRm + ΔVt)",
  "interpretation": "Moderate portability - average impact. This player will likely contribute positively to team value and revenue, but not dramatically.",
  "warnings": []
}
```

### Interpreting the Brand Portability Score (χ)

The χ value quantifies a player's potential impact on team value and revenue when moving to a new market:

| Score Range | Classification | Interpretation |
|-------------|----------------|----------------|
| **χ > 3.0** | Exceptional | Star player with massive market impact. Significant boost to team value and revenue expected. |
| **2.0 < χ ≤ 3.0** | High | Strong positive effect on team value and revenue. |
| **1.0 < χ ≤ 2.0** | Moderate | Average impact. Positive contribution but not dramatic. |
| **0.5 < χ ≤ 1.0** | Low | Limited impact. Minimal effect on team value and revenue. |
| **χ ≤ 0.5** | Minimal | Negligible impact. Unlikely to significantly affect team metrics. |

### Understanding Component Values

**Career Historical Baseline (Ch):**
- Player's average annual commercial output
- Acts as control variable
- Higher values indicate established brand value

**Market Adjustment Factor (Ma):**
- Adjusts for market size and player contribution
- Tier 1 markets: 1.25 (large markets like SF, NY, LA)
- Tier 2 markets: 1.0 (mid-size markets like Seattle, Indiana)
- Tier 3 markets: 0.85 (smaller markets like Dallas, Connecticut)

**Revenue Delta (ΔRm):**
- Change in player-specific revenue in new market vs career average
- Positive values indicate revenue increase in new market
- Components: merchandise sales, TV ratings, ticket premiums

**Team Value Lift (ΔVt):**
- Team's growth rate minus league average growth rate
- Positive values indicate team outperforming league average
- Negative values indicate team underperforming league average

### Warnings and Edge Cases

The calculator may include warnings in the output:

**"Denominator near zero" warning:**
- Occurs when ΔRm + ΔVt ≈ 0
- System applies epsilon adjustment (0.01) to prevent division by zero
- Indicates revenue delta and team value lift are offsetting each other

**"Negative denominator" warning:**
- Occurs when ΔRm + ΔVt < 0
- Both revenue delta and team value lift are negative
- May indicate unfavorable market conditions or negative player impact
- Interpret χ value with caution

---

## 🔧 Data Sources Setup

### Local Data Files (Included)

The following data files are included in the `data/` directory:

1. **Forbes WNBA Team Valuations (2025)**
   - File: `data/Forbes top 12 most valueable wnba teams 2025.csv`
   - Contains: Team valuations, revenue, and ownership data for all 12 WNBA teams

2. **WNBA 2024 Market Tiers**
   - File: `data/WNBA 2024 market tiers data.json`
   - Contains: 2024 team valuations, 2023 revenue, market tier classifications

3. **WNBA 2026 Market Tiers**
   - File: `data/WNBA 2026 Market Tiers.json`
   - Contains: Market tier classifications, DMA rankings, adjustment factors

### External Data Sources (Optional)

For live data integration, the system supports:

**wehoop R Package:**
- Provides WNBA game and player statistics (2002-2024)
- Installation: `install.packages("wehoop")`
- Usage: Requires R and rpy2 Python package

**Statista Data:**
- WNBA viewership, attendance, and salary data
- Manual data entry required (subscription-based source)
- See requirements.md for specific datasets

### Data File Format

**CSV Format (Forbes Valuations):**
```csv
Team,Valuation,Revenue,Owner
Indiana Fever,226000000,32000000,Herb Simon
Las Vegas Aces,400000000,45000000,Mark Davis
...
```

**JSON Format (Market Tiers):**
```json
{
  "tiers": {
    "tier_1": {
      "tier": 1,
      "adjustment_factor": 1.25,
      "teams": ["New York Liberty", "Los Angeles Sparks", ...]
    }
  },
  "team_dma_rankings": {
    "New York Liberty": 1,
    "Los Angeles Sparks": 2,
    ...
  }
}
```

---

## 🧪 Testing

The project includes comprehensive unit tests and property-based tests.

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/test_*.py -k "not property"

# Property-based tests only
pytest tests/test_*_property.py

# Specific module tests
pytest tests/test_brand_portability_calculator.py
```

### Test Coverage

```bash
pytest --cov=src --cov-report=html
```

View coverage report: `open htmlcov/index.html`

---

## 📚 Additional Resources

- **Requirements Document**: [requirements.md](.kiro/specs/brand-portability-formula/requirements.md) - Detailed requirements and user stories
- **Design Document**: [design.md](.kiro/specs/brand-portability-formula/design.md) - System architecture and design decisions
- **Implementation Tasks**: [tasks.md](.kiro/specs/brand-portability-formula/tasks.md) - Development task breakdown
- **Example Script**: [example.py](example.py) - Complete working example with Caitlin Clark scenario

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Submit a pull request

---

## 📄 License

See [LICENSE](LICENSE) file for details.

---

## 🎓 Academic Context

This project was developed as part of **ETM-527-001 Winter 2026** at **Portland State University**.

**Research Context:** [WNBA Financial Reality: Revenue, Losses, and Fair Pay](https://www.youtube.com/watch?v=1KycKWZBLX8)

---