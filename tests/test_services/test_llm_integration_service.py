# tests/test_services/test_llm_integration_service.py

import pytest
from unittest.mock import MagicMock, patch
from app.services.llm_integration_service import get_gemini_chat, get_gemini_response


mock_genai = MagicMock()
mock_model = MagicMock()
mock_genai.GenerativeModel.return_value = mock_model

@patch('app.services.llm_integration_service.genai', mock_genai)
def test_get_gemini_chat():
    chat_mock = MagicMock()
    mock_model.start_chat.return_value = chat_mock

    chat = get_gemini_chat()

    assert chat == chat_mock
    mock_genai.configure.assert_called_once_with(api_key='AIzaSyAOc9Ixda9XeUddNGyqL9RRLvLpDrUZ5DU')
    mock_model.start_chat.assert_called_once_with(history=[])


def test_get_gemini_response():
    chat_mock = MagicMock()
    message = "Hello Gemini!"

    result = get_gemini_response(chat_mock, message)

    assert result
