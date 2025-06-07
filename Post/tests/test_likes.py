import pytest
from Users.models import userBlog, teams
from rest_framework.test import APIClient
from django.db import IntegrityError
from Post.models import Post, Likes

@pytest.fixture
def create_post():  
    team = teams.objects.create(name='Test Team')
    author = userBlog.objects.create_user(username='testuser', password= "123456", team=team)
    return Post.objects.create(
        title="Test Post",
        content="This is a test post.",
        permissions=17, 
        author=author,
    )

@pytest.fixture
def create_many_likes():
    team = teams.objects.create(name='Team-Pagination')
    author = userBlog.objects.create_user(
        username='author_page',
        password='123456',
        team=team,
        email='author_page@example.com'
    )
    post = Post.objects.create(
        title="Post Pagination",
        content="Contenido",
        permissions=17,
        author=author,
    )
    for i in range(25):
        u = userBlog.objects.create_user(
            username=f'user_page_{i}',
            password='123456',
            team=team,
            email=f'user_page_{i}@example.com'
        )
        Likes.objects.create(post=post, user=u)
    return post

def test_createLikes(db,create_post):
    post = create_post
    user = userBlog.objects.create_user(username='liker', password='123456', team=post.author.team, email = "random@gmaill.com")
    client = APIClient()
    client.force_authenticate(user=user)

    payload = {
        "post": post.id,
    }

    response = client.post("/likes/", payload, format='json')

    assert response.status_code == 201
    assert post.likes.count() == 1
    likes = post.likes.first()
    assert likes.user == user

@pytest.mark.django_db(transaction=True)
def test_prevent_duplicate_likes(db, create_post):
    post = create_post
    user = userBlog.objects.create_user(username='liker2', password='123456', team=post.author.team, email="dupkk@gmaill.com")
    client = APIClient()
    client.force_authenticate(user=user)

    payload = {"post": post.id}
    response1 = client.post("/likes/", payload, format='json')

    try:
        client.post("/likes/", payload, format='json')
        assert False
         
    except Exception as e:
        assert True
    assert response1.status_code == 201
    assert post.likes.count() == 1


def test_unauthenticated_cannot_like(db, create_post):
    post = create_post
    client = APIClient()
    payload = {"post": post.id}
    response = client.post("/likes/", payload, format='json')
    assert response.status_code == 403


def test_cantlLikePostWithNoAccess(db):
    team = teams.objects.create(name='Isolated Team')
    author = userBlog.objects.create_user(username='hiddenauthor', password="123456", team=team)
    post = Post.objects.create(
        title="Hidden Post",
        content="You shouldn't see this",
        permissions=1,
        author=author,
    )
    other_team = teams.objects.create(name='Other Team')
    outsider = userBlog.objects.create_user(username='outsider', password="123456", team=other_team, email="aaa@aa.com")
    
    client = APIClient()
    client.force_authenticate(user=outsider)

    response = client.post(f"/likes/", {"post": post.id}, format='json')
    assert response.status_code == 400
    assert post.likes.count() == 0


def test_list_likes(db, create_post):
    post = create_post
    user = userBlog.objects.create_user(username='liker3', password='123456', team=post.author.team, email = "d@gmail.com")
    client = APIClient()
    client.force_authenticate(user=user)
    post2 = Post.objects.create(
        title="Teset Post",
        content="This is a test post.",
        permissions=0, 
        author=post.author,
    )
    Likes.objects.create(post_id = post2.id, user_id = post.author.id)
    client.post("/likes/", {"post": post.id}, format='json')
    response = client.get(f"/likes/?post={post.id}")
    assert response.status_code == 200
    assert len(response.data["result"]) == 1
    

def test_like_nonexistent_post_fails(db):
    user = userBlog.objects.create_user(username='liker', password='123456', team=teams.objects.create(name='T'), email="test@test.com")
    client = APIClient()
    client.force_authenticate(user=user)
    
    response = client.post("/likes/", {"post": 9999}, format='json')
    assert response.status_code == 400


def test_delete_like(db, create_post):
    post = create_post
    user = userBlog.objects.create_user(username='liker4', password='123456', team=post.author.team, email = "del@gañ.com")
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post("/likes/", {"post": post.id}, format='json')
    like_id = response.data['id']

    delete_response = client.delete(f"/likes/{like_id}/")
    assert delete_response.status_code == 204
    assert post.likes.count() == 0 

def test_likeOnFilteredPostwithNoAccess(db):
    team1 = teams.objects.create(name='Team1')
    team2 = teams.objects.create(name='Team2')
    author = userBlog.objects.create_user(username='author', password="123", team=team1, email="author@gmail.com")
    outsider = userBlog.objects.create_user(username='outsider', password="123", team=team2, email = "outsidfer@gmail.coim")

    post = Post.objects.create(
        title="Hidden",
        content="Secret stuff",
        permissions=0,
        author=author
    )

    liker = userBlog.objects.create_user(username='liker', password="123", team=team1, email = "liker@gmail.comn")
    Likes.objects.create(post=post, user=liker)

    client = APIClient()
    client.force_authenticate(user=outsider)
    response = client.get(f"/likes/?post={post.id}")
    assert response.status_code == 200
    assert response.data["result"] == []
    assert response.data["total_count"] == 0

def test_likesFilteredPost(db):
    team1 = teams.objects.create(name='Team1')
    team2 = teams.objects.create(name='Team2')
    author = userBlog.objects.create_user(username='author', password="123", team=team1, email="author@gmail.com")
    outsider = userBlog.objects.create_user(username='outsider', password="123", team=team2, email = "outsidfer@gmail.coim")

    post = Post.objects.create(
        title="Hidden",
        content="Secret stuff",
        permissions=17,
        author=author
    )

    liker = userBlog.objects.create_user(username='liker', password="123", team=team1, email = "liker@gmail.comn")
    Likes.objects.create(post=post, user=liker)

    client = APIClient()
    client.force_authenticate(user=outsider)
    response = client.get(f"/likes/?post={post.id}")
    assert response.status_code == 200
    assert len(response.data["result"]) == 1
    assert response.data["total_count"] == 1

def test_list_likes_by_user(db, create_post):
    post = create_post

    user1 = userBlog.objects.create_user(
        username='liker_user1',
        password='123456',
        team=post.author.team,
        email='liker_user1@example.com'
    )
    user2 = userBlog.objects.create_user(
        username='liker_user2',
        password='123456',
        team=post.author.team,
        email='liker_user2@example.com'
    )

    Like1 = Likes.objects.create(post=post, user=user1)
    Like2 = Likes.objects.create(post=post, user=user2)

    client = APIClient()

    client.force_authenticate(user=user1)
    response = client.get(f"/likes/?user={user1.id}")
    assert response.status_code == 200
    data = response.data
    assert data["total_count"] == 1
    assert data["result"][0]["user"] == user1.id

    response2 = client.get(f"/likes/?user={user2.id}")
    assert response2.status_code == 200
    data2 = response2.data
    assert data2["total_count"] == 1
    assert data2["result"][0]["user"] == user2.id

def test_likes_pagination(db, create_many_likes):
    post = create_many_likes
    client = APIClient()
    user0 = userBlog.objects.get(username='user_page_0')
    client.force_authenticate(user=user0)

    response1 = client.get(f"/likes/?post={post.id}")
    assert response1.status_code == 200
    data1 = response1.data
    assert data1["total_count"] == 25
    assert len(data1["result"]) == 20
    assert data1["next"] is not None 

    next_url = data1["next"]
    response2 = client.get(next_url)
    assert response2.status_code == 200
    data2 = response2.data
    assert data2["total_count"] == 25
    assert len(data2["result"]) == 5
    assert data2["previous"] is not None