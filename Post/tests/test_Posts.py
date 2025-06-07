import pytest
from Users.models import userBlog, teams
from rest_framework.test import APIClient
from Post.models import Post, Likes, Comments
from django.urls import reverse


@pytest.fixture
def create_team():
    return teams.objects.create(name="Equipo Test")

@pytest.fixture
def create_author(create_team):
    return userBlog.objects.create_user(
        username="author",
        password="password123",
        team=create_team,
        email="author@example.com"
    )

@pytest.fixture
def create_many_posts():
    team = teams.objects.create(name="Pagination Team")
    author = userBlog.objects.create_user(username="pagination_user", password="123456", email="paginator@test.com", team=team)

    posts = []
    for i in range(25):
        post = Post.objects.create(
            title=f"Post #{i}",
            content="Contenido de prueba",
            permissions=17,  
            author=author
        )
        posts.append(post)
    return author


@pytest.fixture
def create_many_postsWithNoAccess():
    team = teams.objects.create(name="Pagination Team")
    author = userBlog.objects.create_user(username="pagination_user", password="123456", email="paginator@test.com", team=team)

    posts = []
    for i in range(25):
        post = Post.objects.create(
            title=f"Post #{i}",
            content="Contenido de prueba",
            permissions=0,  
            author=author
        )
        posts.append(post)
    return author


def test_createPost(db):
    team = teams.objects.create(name='Test Team')
    user = userBlog.objects.create_user(username='testuser', password='123456', team=team, email='testuser1@example.com')
    client = APIClient()
    client.force_authenticate(user=user)
    payload = {
        "title": "Mi primer post",
        "content": "Contenido interesante",
        "is_public": 1,           
        "authenticated": 2,       
        "team": 2                 
    }

    response = client.post("/Post/", payload, format='json')

    assert response.status_code == 201
    assert Post.objects.count() == 1
    post = Post.objects.first()
    assert post.title == "Mi primer post"
    assert post.author == user
    assert post.permissions == 1*9 + 2*3 + 2  

def test_postwithnoContent(db):
    team = teams.objects.create(name='Test Team')
    user = userBlog.objects.create_user(username='testuser', password='123456', team=team, email='testuser2@example.com')
    client = APIClient()
    client.force_authenticate(user=user)

    payload = {
    }
    response = client.post("/Post/", payload, format='json')

    assert response.status_code == 400
    assert Post.objects.count() == 0

def test_postWithnoPermissions(db):

    team = teams.objects.create(name='Test Team')
    user = userBlog.objects.create_user(username='testuser', password='123456', team=team, email='testuser2@example.com')
    client = APIClient()
    client.force_authenticate(user=user)

    payload = {
        "title": "Mi primer post",
        "content": "Contenido interesante",
        "is_public": 1,   
        }
    response = client.post("/Post/", payload, format='json')

    assert response.status_code == 400
    assert Post.objects.count() == 0

def test_postwithoutaccess(db):
    client = APIClient()
    payload = {}

    response = client.post("/Post/", payload, format='json')

    assert response.status_code == 400
    assert Post.objects.count() == 0

def test_cant_readPublic(db, create_author):
    teams.objects.create(id=2, name="name")
    author = create_author
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=5,  
        author=author
    )
    client = APIClient()
    url = reverse("Post-detail", args=[post.id])
    response = client.get(url)
    assert response.status_code == 404

def test_canReadPublic(db, create_author):
    team2 = teams.objects.create(id=2, name="name")
    author = create_author
    user = userBlog.objects.create_user(username="other_user", password="password123", team=team2, email='other1@example.com')
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=5,  
        author=author
    )
    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("Post-detail", args=[post.id])
    response = client.get(url)

    assert response.status_code == 200


def test_cant_readAuthenticated(db, create_author):
    team2 = teams.objects.create(id=2, name="name")
    author = create_author
    user = userBlog.objects.create_user(username="other_user", password="password123", team=team2, email='other2@example.com')
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=2,  
        author=author
    )
    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("Post-detail", args=[post.id])
    response = client.get(url)

    assert response.status_code == 404

def test_canReadAuthenticated(db, create_author):
    team2 = teams.objects.create(id=2, name="name")
    author = create_author
    user = userBlog.objects.create_user(username="other_user", password="password123", team=team2, email='other3@example.com')
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=5,  
        author=author
    )
    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("Post-detail", args=[post.id])
    response = client.get(url)

    assert response.status_code == 200

def test_canReadTeam(db, create_author):
    author = create_author
    user = userBlog.objects.create_user(username="other_user", password="password123", team=author.team, email='other4@example.com')
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=1,  
        author=author
    )
    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("Post-detail", args=[post.id])
    response = client.get(url)

    assert response.status_code == 200
    assert response.data["title"] == "Test Post"

def test_privatePost(db, create_author):
    author = create_author
    user = userBlog.objects.create_user(username="other_user", password="password123", team=author.team, email='other5@example.com')
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=0,  
        author=author
    )
    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("Post-detail", args=[post.id])
    response = client.get(url)
    assert response.status_code == 404

def test_edit(db, create_team):
    team = create_team
    author = userBlog.objects.create_user(username="author", password="password123", team=team, email="edit@example.com")

    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=0,  
        author=author
    )
    client = APIClient()
    client.force_authenticate(user=author)

    url = reverse("Post-detail", args=[post.id])
    response = client.patch(url, {
        "title": "Updated Title",
        "content": "Updated Content",
        "is_public": 1,
        "authenticated": 1,
        "team": 2
    }, format="json")

    assert response.status_code == 200
    post.refresh_from_db()
    assert post.title == "Updated Title"
    assert post.content == "Updated Content"
    assert post.permissions == 1*9 + 1*3 + 2

def test_cantEdit(db, create_team, create_author):
    author = create_author
    auxTeam = teams.objects.create(id=2, name="AuxTeam")
    user = userBlog.objects.create_user(username="other_user", password="password123", team=auxTeam, email='cantedit@example.com')
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=2,  
        author=author
    )
    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("Post-detail", args=[post.id])
    response = client.patch(url, {
        "title": "Updated Title",
        "content": "Updated Content",
        "is_public": 1,
        "authenticated": 1,
        "team": 2
    }, format="json")
    assert response.status_code == 404
    response = client.delete(f"/Post/{post.id}/")
    assert response.status_code == 404


def test_canEditTeam(db, create_author, create_team):
    author = create_author
    user = userBlog.objects.create_user(username="user2", password="password123", team=author.team, email='editteam@example.com')
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=2,  
        author=author
    )
    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("Post-detail", args=[post.id])
    response = client.patch(url, {
        "title": "Updated Title",
        "content": "Updated Content",
        "is_public": 1,
        "authenticated": 2,
        "team": 2
    }, format="json")

    assert response.status_code == 200

def test_canEditAuthenticated(db, create_author, create_team):
    team2 = teams.objects.create(id=2, name="team for test")
    author = create_author
    user = userBlog.objects.create_user(username="user2", password="password123", team=team2, email='auth2@example.com')
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=8,  
        author=author
    )
    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("Post-detail", args=[post.id])
    response = client.patch(url, {
        "title": "Updated Title",
        "content": "Updated Content",
        "is_public": 1,
        "authenticated": 2,
        "team": 2
    }, format="json")

    assert response.status_code == 200

def test_confirmCantEditPublic(db, create_author):
    author = create_author
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=37,  
        author=author
    )
    client = APIClient()
    url = reverse("Post-detail", args=[post.id])
    response = client.patch(url, {
        "title": "Updated Title",
        "content": "Updated Content",
        "is_public": 1,
        "authenticated": 1,
        "team": 2
    }, format="json")

    assert response.status_code == 403

def test_deleteAuthor(db, create_author):
    team = teams.objects.create(name='Test Team')
    user = userBlog.objects.create_user(username='testuser', password='123456', team=team, email='delete1@example.com')
    client = APIClient()
    client.force_authenticate(user=user)
    payload = {
        "title": "test post",
        "content": "meh",
        "is_public": 1,
        "authenticated": 2,
        "team": 2
    }

    response = client.post("/Post/", payload, format='json')
    postId = response.data['id']
    response = client.delete(f'/Post/{postId}/')
    assert response.status_code == 204
    assert Post.objects.count() == 0

def test_canDeleteTeam(db, create_author):
    author = create_author
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=2,
        author=author
    )
    user = userBlog.objects.create_user(username='testuser', password='123456', team=author.team, email='delete2@example.com')
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete(f"/Post/{post.id}/")
    assert response.status_code == 204
    assert Post.objects.count() == 0

def test_cantDeleteTeam(db, create_author):
    author = create_author
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=1,
        author=author
    )
    user = userBlog.objects.create_user(username='testuser', password='123456', team=author.team, email='delete3@example.com')
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.delete(f"/Post/{post.id}/")
    assert response.status_code == 404
    assert Post.objects.count() == 1

def test_cantDeleteAuthenticated(db, create_author):
    team = teams.objects.create(id=2, name='Test Team')
    author = create_author
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=2,
        author=author
    )
    user = userBlog.objects.create_user(username='testuser', password='123456', team=team, email='delete4@example.com')
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete(f"/Post/{post.id}/")
    assert response.status_code == 404
    assert Post.objects.count() == 1

def test_canDeleteAuthenticated(db, create_author):
    team = teams.objects.create(id=2, name='Test Team')
    author = create_author
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=8,
        author=author
    )
    user = userBlog.objects.create_user(username='testuser', password='123456', team=team, email='delete5@example.com')
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete(f"/Post/{post.id}/")
    assert response.status_code == 204
    assert Post.objects.count() == 0

def test_cantDeletePublic(db, create_author):
    author = create_author
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=17,
        author=author
    )
    client = APIClient()

    response = client.delete(f"/Post/{post.id}/")
    assert response.status_code == 403
    assert Post.objects.count() == 1


def test_excerpt(db, create_author):
    
    author = create_author
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=17,
        author=author
    )
    assert post.excerpt == "Test Content"

def test_excerptOver200(db, create_author):
    author = create_author
    post = Post.objects.create(
        title="Test Post",
        content="Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum sodales, augue velit cursus nunc, este es mi test de prueba para mi excerpt",
        permissions=300,
        author=author
    )
    assert post.excerpt == post.content[:200]
    assert post.content == "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum sodales, augue velit cursus nunc, este es mi test de prueba para mi excerpt"

def test_excerptUpdateContent(db, create_author):
    author = create_author
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        permissions=17,
        author=author
    )
    client = APIClient()
    client.force_authenticate(user = author)
    payload = {
        "title" : "Test Post excerpt",
        "content": "Test content excerpt after update",
        "is_public": 1,
        "authenticated" : 2,
        "team" : 2
        }   

    result = client.put(f"/Post/{post.id}/", payload, format= "json")
    post = Post.objects.first()
    assert post.excerpt == "Test content excerpt after update"

def test_postDeleteCascadesLikesAndComments(db):
    team = teams.objects.create(id =1, name ="test")
    user = userBlog.objects.create(username='testuser', password='123456', team = team)
    post = Post.objects.create(
        title='Test Post',
        content='Este es un post de prueba con contenido suficiente.',
        permissions=0,
        author=user
    )

    like = Likes.objects.create(post=post, user=user)
    comment = Comments.objects.create(post=post, user=user, content='Comentario de prueba')

    assert Likes.objects.filter(post=post).count() == 1
    assert Comments.objects.filter(post=post).count() == 1

    post.delete()

    assert Likes.objects.count() == 0
    assert Comments.objects.count() == 0

def test_posts_pagination(db, create_many_posts):
    user = create_many_posts
    client = APIClient()
    client.force_authenticate(user=user)

    response1 = client.get("/Post/")  
    assert response1.status_code == 200

    data1 = response1.data
    assert data1["total_count"] == 25
    assert len(data1["result"]) == 10  
    assert data1["next"] is not None

    next_url = data1["next"]
    response2 = client.get(next_url)
    assert response2.status_code == 200

    data2 = response2.data
    assert data2["total_count"] == 25
    assert len(data2["result"]) == 10  
    assert data2["previous"] is not None


    next_url = data2["next"]
    response3 = client.get(next_url)
    assert response3.status_code == 200

    data3 = response3.data
    assert data3["total_count"] == 25
    assert len(data3["result"]) == 5  
    assert data3["next"] is None

def test_postsListWithNoAccess(db, create_many_postsWithNoAccess):
    user = create_many_postsWithNoAccess

    client = APIClient()
    client.force_authenticate(user=user)

    response1 = client.get("/Post/")  
    assert response1.status_code == 200

    data1 = response1.data
    assert data1["total_count"] == 25
    assert len(data1["result"]) == 10  
    assert data1["next"] is not None
    client.logout()
    team = teams.objects.create(id = 2,name="uno") 
    user2 = userBlog.objects.create_user(username ="a", email = "a@gmail.com", team = team)
    client.force_authenticate(user = user2)
    response = client.get("/Post/")
    assert response.status_code == 200
    assert response.data["total_count"] == 0
    assert response.data["result"] == []