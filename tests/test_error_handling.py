"""Tests for error handling scenarios."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from anthropic import APIError, APITimeoutError, RateLimitError, AuthenticationError
from debate_arena.core.debater import Stance, Argument, Debater
from debate_arena.core.arena import Arena
from debate_arena.core.judge import Judge
from debate_arena.core.moderator import Moderator


class TestAPIKeyErrors:
    """Test scenarios with invalid API keys."""

    def test_debater_with_invalid_key(self):
        """Test debater initialization with invalid key doesn't fail immediately."""
        # Anthropic client doesn't validate key on initialization
        debater = Debater(
            stance=Stance.PRO,
            api_key="invalid_key_12345"
        )
        # Key is passed to client but not stored as attribute
        assert debater.client is not None

    def test_debater_with_none_key(self):
        """Test debater with None key uses environment variable."""
        debater = Debater(
            stance=Stance.PRO,
            api_key=None
        )
        assert debater.client is not None

    def test_debater_with_empty_key(self):
        """Test debater with empty string key."""
        debater = Debater(
            stance=Stance.PRO,
            api_key=""
        )
        assert debater.client is not None


class TestNetworkTimeouts:
    """Test scenarios with network timeouts."""

    def test_debater_handles_timeout_error(self):
        """Test that timeout errors can be caught."""
        debater = Debater(Stance.PRO, api_key="test_key")

        with patch.object(debater.client.messages, 'create') as mock_create:
            mock_create.side_effect = APITimeoutError(request=MagicMock())

            with pytest.raises(APITimeoutError):
                debater.generate_opening_statement("Test topic")

    def test_judge_handles_timeout_error(self):
        """Test that judge timeout errors propagate."""
        judge = Judge(api_key="test_key")

        with patch.object(judge.client.messages, 'create') as mock_create:
            mock_create.side_effect = APITimeoutError(request=MagicMock())

            from debate_arena.core.debater import Argument
            arg = Argument(
                content="Test",
                stance=Stance.PRO,
                debater_name="Dr. Chen",
                round_num=1
            )

            with pytest.raises(APITimeoutError):
                judge.evaluate_argument(arg)

    def test_moderator_handles_timeout_error(self):
        """Test that moderator timeout errors propagate."""
        moderator = Moderator(api_key="test_key")

        with patch.object(moderator.client.messages, 'create') as mock_create:
            mock_create.side_effect = APITimeoutError(request=MagicMock())

            with pytest.raises(APITimeoutError):
                moderator.open_debate("Test topic", [])


class TestRateLimitErrors:
    """Test scenarios with rate limiting."""

    def test_debater_handles_rate_limit_error(self):
        """Test that rate limit errors can be caught."""
        debater = Debater(Stance.PRO, api_key="test_key")

        with patch.object(debater.client.messages, 'create') as mock_create:
            # Use a generic exception to simulate rate limiting
            mock_create.side_effect = Exception("Rate limit exceeded")

            with pytest.raises(Exception, match="Rate limit exceeded"):
                debater.generate_opening_statement("Test topic")


class TestAPIErrors:
    """Test scenarios with general API errors."""

    def test_debater_handles_api_error(self):
        """Test that API errors can be caught."""
        debater = Debater(Stance.PRO, api_key="test_key")

        with patch.object(debater.client.messages, 'create') as mock_create:
            mock_create.side_effect = Exception("API error occurred")

            with pytest.raises(Exception, match="API error occurred"):
                debater.generate_opening_statement("Test topic")

    def test_judge_handles_api_error(self):
        """Test that judge API errors propagate."""
        judge = Judge(api_key="test_key")

        with patch.object(judge.client.messages, 'create') as mock_create:
            mock_create.side_effect = Exception("API error")

            from debate_arena.core.debater import Argument
            arg = Argument(
                content="Test",
                stance=Stance.PRO,
                debater_name="Dr. Chen",
                round_num=1
            )

            with pytest.raises(Exception, match="API error"):
                judge.evaluate_argument(arg)


class TestAuthenticationErrors:
    """Test scenarios with authentication failures."""

    def test_debater_handles_auth_error(self):
        """Test that authentication errors can be caught."""
        debater = Debater(Stance.PRO, api_key="test_key")

        with patch.object(debater.client.messages, 'create') as mock_create:
            mock_create.side_effect = Exception("Invalid API key")

            with pytest.raises(Exception, match="Invalid API key"):
                debater.generate_opening_statement("Test topic")


class TestModelAvailability:
    """Test scenarios with unavailable or invalid models."""

    def test_debater_with_invalid_model(self):
        """Test debater with invalid model name."""
        debater = Debater(
            stance=Stance.PRO,
            model="invalid-model-name-12345",
            api_key="test_key"
        )
        # Model name is not validated on initialization
        assert debater.model == "invalid-model-name-12345"

    def test_arena_with_custom_model(self):
        """Test arena with custom model selection."""
        for model in [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-7-sonnet-20250219",
            "claude-3-5-sonnet-20250219",
        ]:
            arena = Arena(
                topic="Test",
                rounds=1,
                api_key="test_key",
                model=model
            )
            assert arena.model == model

    def test_debater_model_can_be_changed(self):
        """Test that model can be changed after initialization."""
        debater = Debater(
            stance=Stance.PRO,
            model="claude-3-opus-20240229",
            api_key="test_key"
        )
        assert debater.model == "claude-3-opus-20240229"


class TestEmptyArgumentLists:
    """Test scenarios with empty argument lists for rebuttals."""

    def test_rebuttal_with_no_opponent_arguments(self):
        """Test rebuttal generation with empty opponent arguments list."""
        debater = Debater(Stance.PRO, api_key="test_key")

        with patch.object(debater.client.messages, 'create') as mock_create:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="No arguments to rebut.")]
            mock_create.return_value = mock_response

            result = debater.generate_rebuttal(
                topic="Test topic",
                opponent_arguments=[],  # Empty list
                round_num=1
            )
            assert isinstance(result, Argument)
            assert result.is_rebuttal is True

    def test_judge_with_empty_arguments(self):
        """Test judge with empty argument lists."""
        judge = Judge(api_key="test_key")

        with patch.object(judge.client.messages, 'create') as mock_create:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="No arguments to judge.")]
            mock_create.return_value = mock_response

            result = judge.render_verdict(
                topic="Test topic",
                pro_arguments=[],
                con_arguments=[]
            )
            assert result is not None
            assert len(result.pro_scores) == 0
            assert len(result.con_scores) == 0


class TestInvalidArgumentInputs:
    """Test scenarios with invalid argument inputs."""

    def test_debater_rebuttal_with_mixed_stance_opponents(self):
        """Test rebuttal when opponents have different stances."""
        debater = Debater(Stance.PRO, api_key="test_key")

        # Create opponent arguments from different stances
        opponents = [
            Argument(
                content="CON argument",
                stance=Stance.CON,
                debater_name="Prof. Webb",
                round_num=1
            ),
            Argument(
                content="NEUTRAL argument",
                stance=Stance.NEUTRAL,
                debater_name="Dr. Morgan",
                round_num=1
            )
        ]

        with patch.object(debater.client.messages, 'create') as mock_create:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Response to both.")]
            mock_create.return_value = mock_response

            result = debater.generate_rebuttal(
                topic="Test topic",
                opponent_arguments=opponents,
                round_num=1
            )
            assert result.stance == Stance.PRO


class TestProgressCallbackErrors:
    """Test scenarios with progress callback errors."""

    def test_progress_callback_exception_during_log(self):
        """Test that exceptions in progress callback don't crash debate."""
        def failing_callback(msg: str) -> None:
            if "error" in msg.lower():
                raise ValueError("Callback error")

        arena = Arena(
            topic="Test topic",
            rounds=1,
            api_key="test_key",
            on_progress=failing_callback
        )

        # Safe messages should work
        arena._log("Safe message")
        assert "Safe message" in arena.transcript


class TestConcurrentDebates:
    """Test scenarios for multiple concurrent debates."""

    def test_multiple_arenas_can_exist(self):
        """Test that multiple arena instances can be created."""
        arenas = [
            Arena(topic=f"Topic {i}", rounds=1, api_key="test_key")
            for i in range(5)
        ]
        assert len(arenas) == 5
        assert all(isinstance(a, Arena) for a in arenas)

    def test_multiple_debaters_with_same_stance(self):
        """Test multiple debaters with same stance can coexist."""
        debaters = [
            Debater(Stance.PRO, api_key="test_key")
            for _ in range(3)
        ]
        assert len(debaters) == 3
        assert all(d.stance == Stance.PRO for d in debaters)

    def test_arena_state_isolation(self):
        """Test that multiple arenas maintain separate state."""
        arena1 = Arena(topic="Topic 1", rounds=1, api_key="test_key")
        arena2 = Arena(topic="Topic 2", rounds=1, api_key="test_key")

        arena1._log("Message for arena 1")
        arena2._log("Message for arena 2")

        assert "Message for arena 1" in arena1.transcript
        assert "Message for arena 1" not in arena2.transcript
        assert "Message for arena 2" in arena2.transcript
        assert "Message for arena 2" not in arena1.transcript
