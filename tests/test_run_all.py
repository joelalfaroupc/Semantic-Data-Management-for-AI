import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.run_all import pipeline_commands, run_pipeline


class RunAllPipelineTest(unittest.TestCase):
    def test_pipeline_commands_run_outputs_in_dependency_order(self):
        commands = pipeline_commands(Path("custom-p1"))

        self.assertEqual(
            commands,
            [
                ["build_kg.py", "--p1-root", "custom-p1"],
                ["run_sparql_analysis.py"],
                ["run_embedding_ml.py"],
                ["build_embedding_dashboard.py"],
            ],
        )

    def test_run_pipeline_invokes_each_script_with_current_python(self):
        with patch("scripts.run_all.subprocess.run") as run:
            run_pipeline(Path("custom-p1"))

        self.assertEqual(run.call_count, 4)
        self.assertEqual(
            [args[0][0][1].name for args in run.call_args_list],
            [
                "build_kg.py",
                "run_sparql_analysis.py",
                "run_embedding_ml.py",
                "build_embedding_dashboard.py",
            ],
        )
        self.assertTrue(all(kwargs == {"check": True} for _, kwargs in run.call_args_list))


if __name__ == "__main__":
    unittest.main()
