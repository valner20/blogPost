import pytest
from Users.models import userBlog, teams
from rest_framework.test import APIClient
from Post.models import Post, Comments

@pytest.fixture
def create_post():  
    team = teams.objects.create(name='Test Team')
    author = userBlog.objects.create_user(
        username='testuser',
        password="123456",
        team=team,
        email='author@test.com'  
    )
    return Post.objects.create(
        title="Test Post",
        content="This is a test post.",
        permissions=17, 
        author=author,
    )

def test_createComment(db, create_post):
    post = create_post
    user = userBlog.objects.create_user(
        username='commenter',
        password='123456',
        team=post.author.team,
        email='commenter1@test.com'  
    )
    client = APIClient()
    client.force_authenticate(user=user)

    payload = {
        "post": post.id,
        "content": "This is a test comment."
    }

    response = client.post("/comment/", payload, format='json')

    assert response.status_code == 201
    assert post.comments.count() == 1
    comment = post.comments.first()
    assert comment.content == "This is a test comment."
    assert comment.user == user


def test_editComment_forbidden(db, create_post):
    post = create_post
    user = userBlog.objects.create_user(
        username='commenter',
        password='123456',
        team=post.author.team,
        email='commenter2@test.com'
    )
    client = APIClient()
    client.force_authenticate(user=user)

    payload = {
        "post": post.id,
        "content": "This is a test comment."
    }

    response = client.post("/comment/", payload, format='json')
    comment_id = response.data['id']
    assert response.status_code == 201

    user2 = userBlog.objects.create_user(
        username='faker',
        password='123456',
        team=post.author.team,
        email='faker@test.com'
    )

    client.force_authenticate(user=user2)
    auxPayLoad = {
        "content": "this is a try"
    }
    response2 = client.put(f"/comment/{comment_id}/", auxPayLoad, format='json')
    assert response2.status_code == 405
    assert post.comments.count() == 1
    comment = post.comments.first()
    assert comment.content == "This is a test comment."
    assert comment.user == user


def test_cantEditCommentByAuthor(db, create_post):
    post = create_post
    user = userBlog.objects.create_user(
        username='commenter',
        password='123456',
        team=post.author.team,
        email='commenter3@test.com'
    )
    client = APIClient()
    client.force_authenticate(user=user)

    payload = {
        "post": post.id,
        "content": "This is a test comment."
    }

    response = client.post("/comment/", payload, format='json')
    comment_id = response.data['id']
    assert response.status_code == 201

    auxPayLoad = {
        "content": "this is a try"
    }
    response2 = client.put(f"/comment/{comment_id}/", auxPayLoad, format='json')
    assert response2.status_code == 405
    assert post.comments.count() == 1
    comment = post.comments.first()
    assert comment.content == "This is a test comment."
    assert comment.user == user


def test_deleteCommentJustAuthor(db, create_post):
    post = create_post
    user = userBlog.objects.create_user(
        username='commenter',
        password='123456',
        team=post.author.team,
        email='commenter4@test.com'
    )
    client = APIClient()
    client.force_authenticate(user=user)

    payload = {
        "post": post.id,
        "content": "This is a test comment."
    }

    response = client.post("/comment/", payload, format='json')
    comment_id = response.data['id']
    assert response.status_code == 201
    response = client.delete(f"/comment/{comment_id}/")
    assert response.status_code == 204
    assert post.comments.count() == 0


def test_cantDeleteComment(db, create_post):
    post = create_post
    user = userBlog.objects.create_user(
        username='commenter',
        password='123456',
        team=post.author.team,
        email='commenter5@test.com'
    )
    client = APIClient()
    client.force_authenticate(user=user)

    payload = {
        "post": post.id,
        "content": "This is a test comment."
    }

    response = client.post("/comment/", payload, format='json')
    comment_id = response.data['id']
    assert response.status_code == 201

    user = userBlog.objects.create_user(
        username='commenter2',
        password='123456',
        team=post.author.team,
        email='commenter6@test.com'
    )

    client.logout()
    client.force_authenticate(user=user)

    response = client.delete(f"/comment/{comment_id}/")
    assert response.status_code == 403
    assert post.comments.count() == 1


def test_listComments(db, create_post):
    post = create_post
    user = userBlog.objects.create_user(
        username='commenter',
        password='123456',
        team=post.author.team,
        email='commenter7@test.com'
    )
    client = APIClient()
    client.force_authenticate(user=user)

    payload = {"post": post.id, "content": "Comment 1"}
    client.post("/comment/", payload, format='json')

    response = client.get(f"/comment/?post={post.id}")
    assert response.status_code == 200


def test_commentWithNoContent(db, create_post):
    post = create_post
    user = userBlog.objects.create_user(
        username='commenter',
        password='123456',
        team=post.author.team,
        email='commenter8@test.com'
    )
    client = APIClient()
    client.force_authenticate(user=user)

    payload = {"post": post.id}
    response = client.post("/comment/", payload, format='json')
    assert response.status_code == 400

def test_commentUnauthenticated(db, create_post):
    post = create_post
    client = APIClient()
    payload = {
        "post": post.id,
        "content": "fail"
    }
    response = client.post("/comment/", payload, format='json')
    assert response.status_code == 403


def test_cantCommentAuth(db):
    team1 = teams.objects.create(name='Team1')
    team2 = teams.objects.create(name='Team2')
    author = userBlog.objects.create_user(username='author', password="123", team=team1, email="author@gmail.com")
    outsider = userBlog.objects.create_user(username='outsider', password="123", team=team2, email = "outsidfer@gmail.coim")

    post = Post.objects.create(
        title="Hidden",
        content="Secret stuff",
        permissions=2,
        author=author
    )

    client = APIClient()
    client.force_authenticate(user = outsider)
    response = client.post("/comment/", {"post": post.id}, format="json")
    assert response.status_code == 400
    assert Comments.objects.count() == 0


def test_cantCommentTeam(db):
    team1 = teams.objects.create(name='Team1')
    author = userBlog.objects.create_user(username='author', password="123", team=team1, email="author@gmail.com")

    post = Post.objects.create(
        title="Hidden",
        content="Secret stuff",
        permissions=0,
        author=author
    )

    commenter = userBlog.objects.create_user(username='commenter', password="123", team=team1, email = "commenter@gmail.comn")
    client = APIClient()
    client.force_authenticate(user = commenter)
    response = client.post("/comment/", {"post": post.id}, format="json")
    assert response.status_code == 400
    assert Comments.objects.count() == 0

def test_delete_nonexistent_comment(db):
    user = userBlog.objects.create_user(
        username='user',
        password='123456',
        team=teams.objects.create(name='Another Team'),
        email='nonexistent2@test.com'
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete("/comment/99999/")
    assert response.status_code == 404

def test_getCommentsfilteredPostWithnoAccess(db):
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

    commenter = userBlog.objects.create_user(username='commenter', password="123", team=team1, email = "commenter@gmail.comn")
    Comments.objects.create(post=post, user=commenter)

    client = APIClient()
    client.force_authenticate(user=outsider)
    response = client.get(f"/comment/?post={post.id}")
    assert response.status_code == 200
    assert response.data["result"] == []
    assert response.data["total_count"] == 0

def test_getCommentsFilteredPostWithAccess(db):
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

    commenter = userBlog.objects.create_user(username='commenter', password="123", team=team1, email = "commenter@gmail.comn")
    Comments.objects.create(post=post, user=commenter)

    client = APIClient()
    client.force_authenticate(user=outsider)
    response = client.get(f"/comment/?post={post.id}")
    assert response.status_code == 200
    assert len(response.data["result"]) == 1
    assert response.data["total_count"] == 1
