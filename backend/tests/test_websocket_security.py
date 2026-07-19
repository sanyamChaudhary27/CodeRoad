from app.api.websocket import token_from_protocol_header


def test_websocket_token_is_extracted_from_dedicated_subprotocol() -> None:
    header = "coderoad, coderoad-auth.header.payload.signature"

    assert token_from_protocol_header(header) == "header.payload.signature"


def test_websocket_token_is_required() -> None:
    assert token_from_protocol_header("coderoad") is None
    assert token_from_protocol_header("coderoad-auth.") is None
