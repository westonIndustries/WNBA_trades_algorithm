# Implementation Plan: Brand Portability Formula

## Overview

This implementation plan breaks down the Brand Portability Formula system into discrete coding tasks. The system calculates χ (chi), measuring a player's potential impact on team value and revenue when traded to a new market using the formula: χ = Ch ⋅ Ma / (ΔRm + ΔVt).

The implementation follows a bottom-up approach: data layer → estimation layer → calculation layer → application layer, with testing integrated throughout.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create Python project structure with src/ and tests/ directories
  - Set up pyproject.toml or requirements.txt with dependencies: pandas, numpy, hypothesis, pytest, rpy2 (for wehoop)
  - Create data models module with dataclasses for PlayerData, TeamData, LeagueData, MarketTierData
  - Set up pytest configuration for unit and property-based tests
  - _Requirements: Data Requirements, Data Format_

- [x] 2. Implement data layer - CSV/JSON loaders
  - [x] 2.1 Implement CSVLoader class
    - Write load_forbes_valuations() method to parse Forbes CSV data
    - Write load_market_tiers() method to parse market tier CSV data
    - Handle file not found and malformed CSV errors with clear messages
    - _Requirements: Data Sources - Forbes WNBA Team Valuations, WNBA 2024 Market Tiers_
  
  - [x] 2.2 Write property test for CSV loader
    - **Property: CSV parsing preserves data integrity**
    - **Validates: Data Requirements - Data Format**
  
  - [x] 2.3 Implement JSONLoader class
    - Write load_market_tiers_2024() method to parse 2024 market tiers JSON
    - Write load_market_tiers_2026() method to parse 2026 market tiers JSON
    - Handle file not found and malformed JSON errors with clear messages
    - _Requirements: Data Sources - WNBA 2024 Market Tiers, WNBA 2026 Market Tiers_
  
  - [x] 2.4 Write unit tests for JSON loader
    - Test with valid JSON files
    - Test error handling for missing files and malformed JSON
    - _Requirements: Data Sources - Local Data Files_

- [x] 3. Implement data layer - external data adapters
  - [x] 3.1 Implement WEHOOPAdapter class
    - Set up rpy2 integration with wehoop R package
    - Write fetch_player_stats() method to get player statistics
    - Write fetch_team_stats() method to get team statistics
    - Handle API unavailable errors with retry logic (3 attempts, exponential backoff)
    - _Requirements: Data Sources - wehoop R Package_
  
  - [x] 3.2 Implement StatistaAdapter class
    - Write get_viewership_data() method (stub for manual data entry)
    - Write get_attendance_data() method (stub for manual data entry)
    - Write get_salary_data() method (stub for manual data entry)
    - Document that Statista data must be manually entered from source
    - _Requirements: Data Sources - WNBA Viewership Data, WNBA Team Attendance Data, WNBA Player Salary Data_
  
  - [x] 3.3 Write integration tests for data adapters
    - Test wehoop adapter with sample queries
    - Test Statista adapter with mock data
    - _Requirements: Data Sources_

- [x] 4. Implement estimation layer
  - [x] 4.1 Implement MerchandiseEstimator class
    - Write estimate_sales() method using formula: (Scoring % × Salary % × Market Tier Factor) × League Revenue Baseline × 0.05
    - Validate input ranges (percentiles 0.0-1.0, market tier factor in [0.85, 1.0, 1.25])
    - _Requirements: Estimation Methods 1, Variable Definitions - ΔRm_
  
  - [x] 4.2 Write property test for merchandise estimator
    - **Property 6: Merchandise sales estimation formula**
    - **Validates: Requirements - Estimation Methods 1**
  
  - [x] 4.3 Implement TVRatingEstimator class
    - Write estimate_impact() method using star power formula
    - Calculate star power score: (Scoring % × 0.4) + (Salary % × 0.3) + (Social Media Index × 0.3)
    - Apply league viewership growth and market reach factor
    - _Requirements: Estimation Methods 3, Variable Definitions - ΔRm_
  
  - [x] 4.4 Write property test for TV rating estimator
    - **Property 8: TV rating impact estimation formula**
    - **Validates: Requirements - Estimation Methods 3**
  
  - [x] 4.5 Implement TicketPremiumEstimator class
    - Write estimate_premium() method using attendance differential formula
    - Calculate attribution factor: (Player Performance Weight) × (Star Power Multiplier)
    - _Requirements: Estimation Methods 4, Variable Definitions - ΔRm_
  
  - [x] 4.6 Write property test for ticket premium estimator
    - **Property 9: Ticket premium estimation formula**
    - **Validates: Requirements - Estimation Methods 4**
  
  - [x] 4.7 Implement PlayerRevenueAttributor class
    - Write calculate_attribution() method using performance weight formula
    - Calculate performance weight: (Player PPG / Team PPG) × 0.6 + (Player Salary / Team Cap) × 0.4
    - Calculate playing time percentage: (Games Played / Total Games) × (Minutes Per Game / 40)
    - _Requirements: Estimation Methods 2, Variable Definitions - ΔRm, Ch_
  
  - [x] 4.8 Write property test for player revenue attributor
    - **Property 7: Player revenue attribution formula**
    - **Validates: Requirements - Estimation Methods 2**

- [x] 5. Checkpoint - Ensure all estimation layer tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement calculation layer - ΔRm module
  - [x] 6.1 Implement RevenueDeltaCalculator class
    - Inject MerchandiseEstimator, TVRatingEstimator, TicketPremiumEstimator dependencies
    - Write calculate() method to compute career average revenue
    - Estimate new city revenue using all three estimators
    - Calculate delta: new city revenue - career average revenue
    - Return RevenueDeltaResult with component breakdown
    - _Requirements: Variable Definitions - ΔRm_
  
  - [x] 6.2 Write property test for revenue delta calculator
    - **Property 2: Revenue delta calculation**
    - **Validates: Requirements - ΔRm Definition**
  
  - [x] 6.3 Write property test for revenue delta components
    - **Property 13: Revenue delta components sum**
    - **Validates: Requirements - ΔRm Definition, Components**
  
  - [x] 6.4 Write unit tests for revenue delta calculator
    - Test with known player and team data
    - Test component breakdown accuracy
    - _Requirements: Variable Definitions - ΔRm_

- [x] 7. Implement calculation layer - ΔVt module
  - [x] 7.1 Implement TeamValueLiftCalculator class
    - Write calculate_league_avg_growth() method using formula: Σ(Team Valuation Change) / Number of Teams / Prior Year Avg Valuation
    - Write calculate() method to compute team's year-over-year valuation change
    - Calculate net lift: team growth rate - league average growth rate
    - Return TeamValueLiftResult with breakdown
    - _Requirements: Variable Definitions - ΔVt, Estimation Methods 5_
  
  - [x] 7.2 Write property test for team value lift calculator
    - **Property 3: Team value lift calculation**
    - **Validates: Requirements - ΔVt Definition**
  
  - [x] 7.3 Write property test for league average growth
    - **Property 10: League average growth rate calculation**
    - **Validates: Requirements - Estimation Methods 5**
  
  - [x] 7.4 Write unit tests for team value lift calculator
    - Test with known valuation histories
    - Test league average calculation with sample data
    - _Requirements: Variable Definitions - ΔVt_

- [x] 8. Implement calculation layer - Ch module
  - [x] 8.1 Implement CareerBaselineCalculator class
    - Inject PlayerRevenueAttributor dependency
    - Write calculate() method to aggregate player career data
    - Calculate annual commercial output for each year
    - Compute arithmetic mean of all annual outputs
    - Return CareerBaselineResult with year-by-year breakdown
    - Handle edge case: zero career baseline should raise exception
    - _Requirements: Variable Definitions - Ch, Edge Cases 1_
  
  - [x] 8.2 Write property test for career baseline calculator
    - **Property 4: Career baseline calculation**
    - **Validates: Requirements - Ch Definition**
  
  - [x] 8.3 Write property test for non-negative career baseline
    - **Property 11: Non-negative career baseline**
    - **Validates: Requirements - Ch Definition, Edge Cases**
  
  - [x] 8.4 Write unit tests for career baseline calculator
    - Test with known career data
    - Test zero career baseline error handling
    - Test with single year vs multiple years of data
    - _Requirements: Variable Definitions - Ch, Edge Cases_

- [x] 9. Implement calculation layer - Ma module
  - [x] 9.1 Implement MarketAdjustmentCalculator class
    - Write calculate() method to get base market tier factor (1.25, 1.0, or 0.85)
    - Apply DMA ranking adjustment
    - Factor in player contribution weight
    - Normalize to ensure fair comparison across markets
    - Return MarketAdjustmentResult with breakdown
    - _Requirements: Variable Definitions - Ma_
  
  - [x] 9.2 Write property test for market adjustment calculator
    - **Property 5: Market adjustment calculation**
    - **Validates: Requirements - Ma Definition**
  
  - [x] 9.3 Write property test for market adjustment factor bounds
    - **Property 12: Market adjustment factor bounds**
    - **Validates: Requirements - Ma Definition**
  
  - [x] 9.4 Write unit tests for market adjustment calculator
    - Test with each market tier (1, 2, 3)
    - Test DMA ranking adjustments
    - Test player contribution weight integration
    - _Requirements: Variable Definitions - Ma_

- [x] 10. Checkpoint - Ensure all calculation layer tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement application layer - formula calculator
  - [x] 11.1 Implement BrandPortabilityCalculator class
    - Inject all four calculator dependencies (ΔRm, ΔVt, Ch, Ma)
    - Write calculate_portability() method to orchestrate all calculations
    - Implement _handle_edge_cases() method for division by zero, negative denominator
    - Apply formula: χ = Ch ⋅ Ma / (ΔRm + ΔVt)
    - Return BrandPortabilityResult with all intermediate values and warnings
    - _Requirements: Formula, Acceptance Criteria 2, Edge Cases_
  
  - [x] 11.2 Write property test for formula calculation
    - **Property 1: Formula calculation correctness**
    - **Validates: Requirements - Acceptance Criteria 2**
  
  - [x] 11.3 Write property test for positive denominator handling
    - **Property 14: Positive denominator handling**
    - **Validates: Requirements - Edge Cases, Acceptance Criteria 4**
  
  - [x] 11.4 Write unit tests for edge cases
    - Test division by zero (ΔRm + ΔVt = 0) applies epsilon and warns
    - Test negative denominator (ΔRm + ΔVt < 0) calculates and warns
    - Test zero career baseline raises exception
    - _Requirements: Edge Cases 1, 2, 4_

- [x] 12. Implement application layer - result formatter
  - [x] 12.1 Implement ResultFormatter class
    - Write to_json() method to serialize result to JSON string
    - Write to_dict() method to convert result to dictionary
    - Write to_readable_text() method for human-readable output
    - Write generate_interpretation() method with chi value ranges
    - Interpretation ranges: >3.0 exceptional, 2.0-3.0 high, 1.0-2.0 moderate, 0.5-1.0 low, ≤0.5 minimal
    - _Requirements: Output Requirements, Example Output Format_
  
  - [x] 12.2 Write property test for output structure
    - **Property 15: Output structure completeness**
    - **Validates: Requirements - Output Requirements, Acceptance Criteria 5**
  
  - [x] 12.3 Write unit tests for result formatter
    - Test JSON serialization with sample results
    - Test interpretation generation for each chi range
    - Test readable text formatting
    - _Requirements: Output Requirements, Acceptance Criteria 5_

- [x] 13. Implement CLI interface
  - [x] 13.1 Create command-line interface
    - Use argparse or click for CLI argument parsing
    - Accept player ID, new team ID, and data file paths as arguments
    - Load data from specified sources
    - Calculate brand portability
    - Output formatted results (JSON or readable text based on flag)
    - Handle errors gracefully with user-friendly messages
    - _Requirements: Output Requirements_
  
  - [x] 13.2 Write integration tests for CLI
    - Test end-to-end calculation with sample data files
    - Test error handling for missing files
    - Test output format options
    - _Requirements: Acceptance Criteria 2, 5_

- [x] 14. Add validation and quality assurance
  - [x] 14.1 Implement validation methods
    - Write attendance_correlation_analysis() to compare estimates with actual data
    - Write valuation_jump_analysis() to validate star player impact
    - Write revenue_multiple_consistency() to check revenue/valuation ratios
    - Write market_tier_consistency() to validate tier adjustments
    - Write peer_comparison() to flag outliers
    - _Requirements: Validation Methods_
  
  - [x] 14.2 Write unit tests for validation methods
    - Test correlation calculations
    - Test outlier detection
    - Test consistency checks
    - _Requirements: Validation Methods_

- [x] 15. Create example usage and documentation
  - [x] 15.1 Create example script
    - Write example.py demonstrating typical usage
    - Include Caitlin Clark to Indiana Fever scenario as example
    - Show how to load data, calculate portability, and interpret results
    - _Requirements: User Stories 1, 2, 3, 4_
  
  - [x] 15.2 Write README documentation
    - Document installation instructions
    - Document data source setup (wehoop, local files)
    - Document CLI usage with examples
    - Document API usage for programmatic access
    - Include interpretation guide for chi values
    - _Requirements: Output Requirements, Acceptance Criteria 5_

- [x] 16. Final checkpoint - Run all tests and validate
  - Run full test suite (unit tests and property tests)
  - Verify all 15 correctness properties pass
  - Test with real 2024-2025 WNBA data
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- Python is the chosen implementation language due to strong data science ecosystem and R integration
- The implementation follows a bottom-up approach to enable incremental testing
