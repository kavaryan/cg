import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the debate_tournament directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'debate_tournament'))

from tournament.tournament_runner import TournamentRunner


class TestTournamentRunner(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.runner = TournamentRunner(
            debater1_type="true-mcts",
            debater1_max_depth=10,
            debater2_type="baseline",
            debater2_max_depth=None
        )
    
    def test_init(self):
        """Test TournamentRunner initialization."""
        self.assertEqual(self.runner.debater1_type, "true-mcts")
        self.assertEqual(self.runner.debater1_max_depth, 10)
        self.assertEqual(self.runner.debater2_type, "baseline")
        self.assertIsNone(self.runner.debater2_max_depth)
        self.assertEqual(self.runner.results, [])
        self.assertEqual(self.runner.output_lines, [])
    
    @patch('debaters.baseline_debater.BaselineDebater')
    def test_create_debater_baseline(self, mock_baseline):
        """Test creating a baseline debater."""
        mock_instance = Mock()
        mock_baseline.return_value = mock_instance
        
        result = self.runner.create_debater("baseline", "pro", "test motion", None)
        
        mock_baseline.assert_called_once_with("pro", "test motion")
        self.assertEqual(result, mock_instance)
    
    @patch('debaters.prompt_mcts_debater.PromptMCTSDebater')
    def test_create_debater_prompt_mcts(self, mock_prompt_mcts):
        """Test creating a prompt-mcts debater."""
        mock_instance = Mock()
        mock_prompt_mcts.return_value = mock_instance
        
        result = self.runner.create_debater("prompt-mcts", "con", "test motion", 5)
        
        mock_prompt_mcts.assert_called_once_with("con", "test motion", k=5)
        self.assertEqual(result, mock_instance)
    
    @patch('debaters.true_mcts_debater.TrueMCTSDebater')
    def test_create_debater_true_mcts(self, mock_true_mcts):
        """Test creating a true-mcts debater."""
        mock_instance = Mock()
        mock_true_mcts.return_value = mock_instance
        
        result = self.runner.create_debater("true-mcts", "pro", "test motion", 20)
        
        mock_true_mcts.assert_called_once_with("pro", "test motion", iterations=20)
        self.assertEqual(result, mock_instance)
    
    def test_create_debater_invalid_type(self):
        """Test creating debater with invalid type raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.runner.create_debater("invalid-type", "pro", "test motion", None)
        
        self.assertIn("Unknown debater type: invalid-type", str(context.exception))
    
    @patch('tournament.tournament_runner.TournamentRunner.create_debater')
    def test_create_debater_pairs(self, mock_create_debater):
        """Test creating debater pairs for a motion."""
        mock_pro = Mock()
        mock_con = Mock()
        mock_create_debater.side_effect = [mock_pro, mock_con]
        
        pairs = self.runner.create_debater_pairs("test motion")
        
        self.assertEqual(len(pairs), 1)
        label, pro_debater, con_debater = pairs[0]
        self.assertEqual(label, "TRUE-MCTS vs BASELINE")
        self.assertEqual(pro_debater, mock_pro)
        self.assertEqual(con_debater, mock_con)
        
        # Verify create_debater was called correctly
        mock_create_debater.assert_any_call("true-mcts", "pro", "test motion", 10)
        mock_create_debater.assert_any_call("baseline", "con", "test motion", None)
    
    @patch('tournament.tournament_runner.MOTIONS', ["Test motion 1", "Test motion 2"])
    @patch('tournament.tournament_runner.NUM_MATCHES', 2)
    @patch('tournament.tournament_runner.SLEEP_SEC', 0)
    @patch('tournament.tournament_runner.DebateMatch')
    @patch('tournament.tournament_runner.TournamentRunner.create_debater_pairs')
    @patch('builtins.print')
    @patch('tournament.tournament_runner.tqdm')
    def test_run_tournament(self, mock_tqdm, mock_print, mock_create_pairs, mock_debate_match):
        """Test running a full tournament."""
        # Mock the progress bar
        mock_tqdm.return_value = range(2)
        
        # Mock debater pairs
        mock_pro = Mock()
        mock_con = Mock()
        mock_create_pairs.return_value = [("TEST vs BASELINE", mock_pro, mock_con)]
        
        # Mock debate results - all matches have pro win (winner "A")
        mock_debate_match.play.return_value = ({"winner": "A"}, ["log1"])
        
        self.runner.run_tournament()
        
        # Verify results
        self.assertEqual(len(self.runner.results), 2)  # 2 motions
        
        # Check first motion result
        motion1, label1, win_rate1 = self.runner.results[0]
        self.assertEqual(motion1, "Test motion 1")
        self.assertEqual(label1, "TEST vs BASELINE")
        self.assertEqual(win_rate1, 1.0)  # All matches won by pro
        
        # Check second motion result
        motion2, label2, win_rate2 = self.runner.results[1]
        self.assertEqual(motion2, "Test motion 2")
        self.assertEqual(label2, "TEST vs BASELINE")
        self.assertEqual(win_rate2, 1.0)  # All matches won by pro
    
    @patch('tournament.tournament_runner.MOTIONS', ["Test motion"])
    @patch('tournament.tournament_runner.NUM_MATCHES', 1)
    @patch('tournament.tournament_runner.DebateMatch')
    @patch('tournament.tournament_runner.TournamentRunner.create_debater_pairs')
    @patch('builtins.print')
    @patch('tournament.tournament_runner.tqdm')
    def test_run_tournament_with_exception(self, mock_tqdm, mock_print, mock_create_pairs, mock_debate_match):
        """Test tournament handles exceptions gracefully."""
        mock_tqdm.return_value = range(1)
        
        mock_pro = Mock()
        mock_con = Mock()
        mock_create_pairs.return_value = [("TEST vs BASELINE", mock_pro, mock_con)]
        
        # Mock an exception during debate
        mock_debate_match.play.side_effect = Exception("API Error")
        
        # Should not raise exception
        self.runner.run_tournament()
        
        # Should have empty results due to exception
        self.assertEqual(len(self.runner.results), 1)
        motion, label, win_rate = self.runner.results[0]
        self.assertEqual(win_rate, 0.0)  # No wins due to exception
    
    def test_run_tournament_with_output_file(self):
        """Test tournament saves results to output file."""
        runner = TournamentRunner(output_file="test_output.txt")
        runner.output_lines = ["Test line 1", "Test line 2"]
        
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            with patch('tournament.tournament_runner.MOTIONS', []):
                runner.run_tournament()
            
            mock_file.assert_called_once_with("test_output.txt", "w")
            mock_file().write.assert_called_once_with("Test line 1\nTest line 2")
    
    @patch('builtins.print')
    def test_print_results(self, mock_print):
        """Test printing tournament results."""
        self.runner.results = [
            ("Motion 1", "LABEL 1", 0.75),
            ("Motion 2", "LABEL 2", 0.50)
        ]
        
        self.runner.print_results()
        
        # Verify print was called with expected format
        mock_print.assert_any_call("\n===== Win-rate summary =====")
        mock_print.assert_any_call("Motion 1                                 LABEL 1                   75.0%")
        mock_print.assert_any_call("Motion 2                                 LABEL 2                   50.0%")
    
    @patch('tournament.tournament_runner.MOTIONS', ["Test motion for sample"])
    @patch('tournament.tournament_runner.TrueMCTSDebater')
    @patch('tournament.tournament_runner.BaselineDebater')
    @patch('tournament.tournament_runner.DebateMatch')
    @patch('builtins.print')
    def test_run_sample_debate(self, mock_print, mock_debate_match, mock_baseline, mock_true_mcts):
        """Test running a sample debate."""
        # Mock debaters
        mock_true_instance = Mock()
        mock_baseline_instance = Mock()
        mock_true_mcts.return_value = mock_true_instance
        mock_baseline.return_value = mock_baseline_instance
        
        # Mock debate result
        mock_verdict = {"winner": "A", "score_A": 8, "score_B": 6}
        mock_log = ["Turn 1: Pro argument", "Turn 2: Con argument", "Turn 3: Pro rebuttal"]
        mock_debate_match.play.return_value = (mock_verdict, mock_log)
        
        self.runner.run_sample_debate()
        
        # Verify debaters were created correctly
        mock_true_mcts.assert_called_once_with("pro", "Test motion for sample")
        mock_baseline.assert_called_once_with("con", "Test motion for sample")
        
        # Verify debate was played
        mock_debate_match.play.assert_called_once_with(
            "Test motion for sample", mock_true_instance, mock_baseline_instance
        )
        
        # Verify output was printed (check that print was called with expected content)
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        self.assertIn("\nSample debate – TRUE-MCTS vs BASELINE\n" + "-" * 60, print_calls)
        
        # The log entries are printed as a single string with newlines
        log_output = "Turn 1: Pro argument\nTurn 2: Con argument\nTurn 3: Pro rebuttal"
        self.assertIn(log_output, print_calls)
    
    @patch('tournament.tournament_runner.MOTIONS', ["Test motion"])
    @patch('tournament.tournament_runner.TrueMCTSDebater')
    @patch('builtins.print')
    def test_run_sample_debate_with_exception(self, mock_print, mock_true_mcts):
        """Test sample debate handles exceptions gracefully."""
        # Mock an exception during debater creation
        mock_true_mcts.side_effect = Exception("Debater creation failed")
        
        self.runner.run_sample_debate()
        
        # Should print error message (check if any print call contains the error)
        print_calls = [str(call) for call in mock_print.call_args_list]
        error_found = any("Debater creation failed" in call for call in print_calls)
        self.assertTrue(error_found, f"Expected error message not found in print calls: {print_calls}")


if __name__ == '__main__':
    unittest.main()
