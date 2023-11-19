

import requests
import random
import string
import pytest

class TestNotesAPI:
    base_url = "https://practice.expandtesting.com/notes/api"
    user_register_url = "/users/register"
    user_login_url = "/users/login"
    notes_url = "/notes"

    # Method to generate a random string
    @staticmethod
    def generate_random_string(length=10):
        characters = string.ascii_letters
        return ''.join(random.choice(characters) for _ in range(length))

    # Function-scoped fixture to register a user and return user credentials
    @pytest.fixture(scope="session")
    def registered_user(self):
        name = self.generate_random_string()
        email = f"{name}@gmail.com"
        password = f"{name}1234567"
        payload = {"name": name, "email": email, "password": password}

        # Register the user
        response_register = requests.post(self.base_url + self.user_register_url, json=payload)
        assert response_register.status_code == 201

        return {"name": name, "email": email, "password": password}

    # Session-scoped fixture to log in and retrieve the user token
    @pytest.fixture(scope="session")
    def session_user_token(self, registered_user):
        email, password = registered_user["email"], registered_user["password"]
        login_payload = {"email": email, "password": password}

        # Log in and retrieve the token
        response_login = requests.post(self.base_url + self.user_login_url, json=login_payload)
        assert response_login.status_code == 200

        return response_login.json()["data"]["token"]

    # Function-scoped fixture to store the list of note IDs
    @pytest.fixture(scope="session")
    def notes_id_list(self, session_user_token):
        ids = []

        for _ in range(5):
            note_data = {"title": "Test Note", "description": "This is a test note.", "category": "Home"}
            headers = {"x-auth-token": session_user_token}

            # Create a note
            response_create_note = requests.post(self.base_url + self.notes_url, json=note_data, headers=headers)
            assert response_create_note.status_code == 200

            # Store the ID in the list
            note_id = response_create_note.json()["data"]["id"]
            ids.append(str(note_id))  # Convert the ID to string

        return ids

    # Fixture to dynamically generate test parameters
    @pytest.fixture(params=range(5))
    def created_note_id(self, request, notes_id_list):
        return notes_id_list[request.param]

    # Get a specific note by its ID
    def test_get_note_by_id(self, session_user_token, created_note_id):
        headers = {"x-auth-token": session_user_token}
        response_note_data = requests.get(self.base_url + self.notes_url + f"/{created_note_id}", headers=headers)
        assert response_note_data.status_code == 200

    # PUT REQUEST: Update a note by its ID
    def test_update_note_by_id(self, session_user_token, created_note_id):
        note_data = {"title": "Updated Note", "description": "Updated description", "completed": True,
                     "category": "Work"}
        headers = {"x-auth-token": session_user_token}
        response_note_data = requests.put(
            self.base_url + self.notes_url + f"/{created_note_id}", headers=headers, json=note_data
        )
        assert response_note_data.status_code == 200

    # PATCH REQUEST: Partially update a note by its ID
    def test_partial_update_note_by_id(self, session_user_token, created_note_id):
        note_data = {"completed": False}
        headers = {"x-auth-token": session_user_token}
        response_note_data = requests.patch(
            self.base_url + self.notes_url + f"/{created_note_id}", headers=headers, json=note_data
        )
        assert response_note_data.status_code == 200

    # Delete a note with the specified ID
    def test_delete_note_by_id(self, session_user_token, created_note_id):
        headers = {"x-auth-token": session_user_token}
        response_note_data = requests.delete(
            self.base_url + self.notes_url + f"/{created_note_id}", headers=headers
        )
        assert response_note_data.status_code == 200


