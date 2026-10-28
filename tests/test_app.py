from copy import deepcopy

import pytest


def test_root_redirects_to_frontend(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_details(client, activities_data):
    # Arrange
    expected = deepcopy(activities_data)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_signup_adds_participant_once(client, activities_data):
    # Arrange
    email = "new+student@mergington.edu"
    expected = deepcopy(activities_data)
    expected["Chess Club"]["participants"].append(email)

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert activities_data == expected
    assert client.get("/activities").json() == expected


def test_signup_rejects_duplicate_without_changing_data(client, activities_data):
    # Arrange
    email = activities_data["Chess Club"]["participants"][0]
    expected = deepcopy(activities_data)

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already registered for this activity"}
    assert activities_data == expected


@pytest.mark.parametrize("method", ["POST", "DELETE"])
def test_unknown_activity_returns_not_found(client, activities_data, method):
    # Arrange
    expected = deepcopy(activities_data)
    email = "student@mergington.edu"

    # Act
    response = client.request(
        method, "/activities/Unknown Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities_data == expected


@pytest.mark.parametrize("method", ["POST", "DELETE"])
def test_missing_email_returns_validation_error(client, activities_data, method):
    # Arrange
    expected = deepcopy(activities_data)
    url = "/activities/Chess Club/signup"

    # Act
    response = client.request(method, url)

    # Assert
    assert response.status_code == 422
    assert any(
        error["loc"] == ["query", "email"]
        for error in response.json()["detail"]
    )
    assert activities_data == expected


def test_unregister_removes_only_selected_participant(client, activities_data):
    # Arrange
    email = activities_data["Chess Club"]["participants"][0]
    expected = deepcopy(activities_data)
    expected["Chess Club"]["participants"].remove(email)

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert activities_data == expected
    assert client.get("/activities").json() == expected


def test_unregister_unknown_participant_preserves_data(client, activities_data):
    # Arrange
    expected = deepcopy(activities_data)
    email = "unknown@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not registered for this activity"}
    assert activities_data == expected


def test_unregister_twice_returns_not_found(client, activities_data):
    # Arrange
    email = activities_data["Chess Club"]["participants"][0]
    url = "/activities/Chess Club/signup"
    client.delete(url, params={"email": email}).raise_for_status()
    expected = deepcopy(activities_data)

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not registered for this activity"}
    assert activities_data == expected


def test_participant_can_sign_up_again_after_unregistering(client, activities_data):
    # Arrange
    email = "returning+student@mergington.edu"
    url = "/activities/Art Club/signup"
    expected = deepcopy(activities_data)
    expected["Art Club"]["participants"].append(email)
    client.post(url, params={"email": email}).raise_for_status()
    client.delete(url, params={"email": email}).raise_for_status()
    assert client.get("/activities").json()["Art Club"]["participants"] == []

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Art Club"}
    assert activities_data == expected
    assert client.get("/activities").json() == expected