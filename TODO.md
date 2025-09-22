ut does now it f# Debate Tournament Codebase Analysis and Fixes

## Issues Found and Fixed

### 1. API Call Tracking Issue ✅ FIXED
**Problem**: The main.py file had hardcoded logic for estimating API calls: `~{max(args.debater1_iterations, args.debater2_iterations) + 15}` which was inaccurate.

**Fix**: 
- Updated `main.py` to use actual API call statistics from `api_client.get_call_statistics()`
- Now prints the actual breakdown of API calls by type (inference, scoring, judge)
- Only shows the estimate for dry-run mode

**Files Modified**:
- `debate_tournament/main_fixed.py` - Fixed version with actual API call statistics

### 2. Missing call_type Parameter in MCTS Algorithm ✅ FIXED
**Problem**: The MCTS algorithm was not passing the `call_type` parameter to API calls, making it impossible to track different types of API calls.

**Fix**:
- Updated `generate_candidate_actions()` method to pass `call_type='inference'`
- Updated `simulate_random_playout()` method to pass `call_type='inference'`

**Files Modified**:
- `debate_tournament/mcts/algorithm_fixed.py` - Fixed version with proper call_type tracking

### 3. API Client Call Tracking ✅ ALREADY IMPLEMENTED
**Status**: The API client already has proper call tracking implemented with `get_call_statistics()` method.

**Current Implementation**:
- Tracks calls by type: 'inference', 'scoring', 'judge'
- Provides `get_call_statistics()` method that returns a dictionary with counts
- Already properly implemented in `debate_tournament/core/api_client.py`

### 4. Other Files Verified ✅
**Files Checked**:
- `debate_tournament/debaters/baseline_debater.py` - ✅ No issues found
- `debate_tournament/debaters/prompt_mcts_debater.py` - ✅ No issues found
- `debate_tournament/debaters/base_debater.py` - ✅ No issues found
- `debate_tournament/utils/scoring.py` - ✅ Already has proper call_type='scoring'
- `debate_tournament/utils/judge.py` - ✅ Already has proper call_type='judge'
- `debate_tournament/tournament/tournament_runner.py` - ✅ No issues found
- `debate_tournament/mcts/node.py` - ✅ No issues found

## Summary

The main issues were:
1. **API call estimation was hardcoded and inaccurate** - Fixed by using actual statistics
2. **MCTS algorithm wasn't tracking call types** - Fixed by adding call_type parameters

All other files in the codebase appear to be correctly implemented with proper error handling and logic.

## Testing Recommendations

1. Run the tournament with different debater configurations to verify API call tracking
2. Test both dry-run and live modes to ensure statistics are accurate
3. Verify that the printed statistics match the actual API usage
