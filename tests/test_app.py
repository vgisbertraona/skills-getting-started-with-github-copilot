import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Verificar que tenemos la estructura esperada
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    
    # Verificar la estructura de una actividad
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_success():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new.student@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "new.student@mergington.edu" in data["message"]

def test_signup_activity_not_found():
    response = client.post(
        "/activities/NonexistentClub/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_signup_full_activity():
    # Primero llenar el club de ajedrez
    chess_club = activities["Chess Club"]
    original_participants = chess_club["participants"].copy()
    
    try:
        # Llenar la actividad hasta el máximo
        while len(chess_club["participants"]) < chess_club["max_participants"]:
            chess_club["participants"].append(f"student{len(chess_club['participants'])}@mergington.edu")
        
        # Intentar registrar un estudiante más
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "one.more@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Activity is full" in data["detail"]
    finally:
        # Restaurar el estado original
        chess_club["participants"] = original_participants

def test_signup_duplicate_email():
    # Intentar registrar un email que ya está registrado
    existing_email = activities["Chess Club"]["participants"][0]
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": existing_email}
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]