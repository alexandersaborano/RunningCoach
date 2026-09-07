import unittest
from unittest.mock import Mock

from core.ai_coach import AICoach


class AICoachFeedbackTests(unittest.TestCase):
    def test_pre_analysis_feedback_is_included_in_prompt(self):
        coach = AICoach.__new__(AICoach)
        coach.client = Mock()
        coach.model_id = "test-model"
        coach.memory_manager = None
        coach.client.models.generate_content.return_value = Mock(text="análise")

        coach.analisar_sessao(
            "sessão de teste",
            feedback_atleta="Senti fadiga na subida final.",
        )

        prompt = coach.client.models.generate_content.call_args.kwargs["contents"]
        self.assertIn("Senti fadiga na subida final.", prompt)
        self.assertIn("FEEDBACK DO ATLETA ANTES DA ANÁLISE", prompt)


if __name__ == "__main__":
    unittest.main()
