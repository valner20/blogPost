import pytest
from Users.models import userBlog,teams
from rest_framework.test import APIClient

def test_register(db):
    client = APIClient()
    team = teams.objects.create(id = 1, name="Equipo Prueba")
    payload = {
            "username": "pedroparamo",
            "password": "password test.",
            "email": "xdxdxdxd@gmail.com",
        }
    result = client.post("/register/", payload, format='json')
    assert result.status_code == 201
    assert userBlog.objects.count() == 1
    user = userBlog.objects.first()
    assert user.username == "pedroparamo"
    assert user.email    == "xdxdxdxd@gmail.com"


def test_registerWrongByUserduplicated(db):
    client = APIClient()
    team = teams.objects.create(id = 1, name="Equipo Prueba")
    payload = {
            "username": "pedroparamo",
            "password": "password test.",
            "email": "xdxdxdxd@gmail.com",
        }
    result = client.post("/register/", payload, format='json')
    assert result.status_code == 201
    result = client.post("/register/", payload, format='json')
    assert result.status_code == 400
    assert userBlog.objects.count() == 1
    user = userBlog.objects.first()
    assert user.username == "pedroparamo"
    assert user.email    == "xdxdxdxd@gmail.com"
    assert userBlog.objects.count() == 1


def test_registeDuplicateEmail(db):
    client = APIClient()
    team = teams.objects.create(id=1, name="Equipo Prueba")
    userBlog.objects.create_user(username="uno", email="email@x.com", password="1234")
    payload = {
        "username": "otro",
        "password": "1234",
        "email": "email@x.com"
    }
    response = client.post("/register/", payload, format="json")
    assert response.status_code == 400
    assert userBlog.objects.count() == 1


def test_registerDefaultTeam(db):
    team = teams.objects.create(id=1, name="Equipo Prueba")
    client = APIClient()
    payload = {
        "username": "pedro",
        "password": "1234",
        "email": "pedro@x.com"
    }
    response = client.post("/register/", payload, format='json')
    user = userBlog.objects.first()
    assert user.team.id == 1

def test_without_password(db): 
    client = APIClient()
    team = teams.objects.create(id = 1, name="Equipo Prueba")
    payload = {
            "username": "pedroparamo",
            "email": "xdxdxdxd@gmail.com",
        }
    result = client.post("/register/", payload, format='json')
    assert result.status_code == 400
    assert userBlog.objects.count() == 0
     

def test_without_username(db):
    client = APIClient()
    team = teams.objects.create(id = 1, name="Equipo Prueba")
    payload = {
            "password": "password test.",
            "email": "xdxdxdxd@gmail.com",
        }
    result = client.post("/register/", payload, format='json')
    assert result.status_code == 400
    assert userBlog.objects.count() == 0


def test_withNothing(db):

    client = APIClient()
    team = teams.objects.create(id = 1, name="Equipo Prueba")
    payload = {
        }
    result = client.post("/register/", payload, format='json')
    assert result.status_code == 400
    assert userBlog.objects.count() == 0


def test_userTryngtoPutRole(db):
    client = APIClient()
    team = teams.objects.create(id = 1, name="Equipo Prueba")
    payload = {
            "username": "pedroparamo",
            "password": "password test.",
            "email": "xdxdxdxd@gmail.com",
            "role" : 'admin'
        }
    result = client.post("/register/", payload, format='json')
    assert result.status_code == 201
    assert userBlog.objects.count() == 1
    user = userBlog.objects.first()
    assert user.username == "pedroparamo"
    assert user.email == "xdxdxdxd@gmail.com"
    assert user.role == "blogger"


def test_passwordIsHashed(db):
    client = APIClient()
    team = teams.objects.create(id = 1, name="Equipo Prueba")
    payload = {
            "username": "pedroparamo",
            "password": "password test.",
            "email": "xdxdxdxd@gmail.com",
        }
    result = client.post("/register/", payload, format='json')
    assert result.status_code == 201
    assert userBlog.objects.count() == 1
    user = userBlog.objects.first()
    assert user.password != 'password test.'
    assert user.check_password('password test.') == True


def test_login(db):
    team = teams.objects.create(id = 1, name="Equipo Prueba")
    user = userBlog.objects.create_user(username = "xd", password = "zapata", email = "xdxd")
    client = APIClient()
    result = client.login(username = "xdxd", password = "zapata")
    assert result is True

def test_TeamCascade(db):
    team = teams.objects.create(id = 1, name="Equipo Prueba")
    team2 = teams.objects.create(id = 2, name="try")

    user = userBlog.objects.create_user(username = "xd", password = "zapata", email = "xdxd", team = team2)
    team2.delete()
    user.refresh_from_db()
    assert user.team.name == "Equipo Prueba"
    assert user.team.id == 1
    

def test_wrongPassword(db):
    team = teams.objects.create(id = 1, name="Equipo Prueba")
    user = userBlog.objects.create(username = "xd", password = "zapata")
    client = APIClient()
    result = client.login(username = "xd", password = "xdxd")
    assert result is False


def test_loginWithNothing(db):
    team = teams.objects.create(id = 1, name="Equipo Prueba")
    user = userBlog.objects.create(username = "xd", password = "zapata")
    client = APIClient()
    result = client.login()
    assert result is False


def test_wrongUsername(db):
    team = teams.objects.create(id = 1, name="Equipo Prueba")
    user = userBlog.objects.create(username = "xd", password = "zapata")
    client = APIClient()
    result = client.login(username = "x", password = "zapata")
    assert result is False


def test_register_alreadylogged(db):
    client = APIClient()
    user = userBlog.objects.create(username = "xd", password = "zapata")
    client.force_authenticate(user = user)
    payload = {
            "username": "pedroparamo",
            "password": "password test.",
            "email": "xdxdxdxd@gmail.com",
        }
    result = client.post("/register/", payload, format='json')
    assert result.status_code == 403
    assert userBlog.objects.count() == 1
    user = userBlog.objects.first()
    assert user.username == "xd"

