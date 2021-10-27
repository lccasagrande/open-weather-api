from api.schemas import UserRequest


def test_user_request():
    x = UserRequest(user_id="1")

    assert x.user_id == 1
