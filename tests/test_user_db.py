from gellish_communicator.SystemUsers import UserDb


def test_creation():
    user_db = UserDb()
    assert user_db.pw_dict == {}
    assert user_db.users == []
