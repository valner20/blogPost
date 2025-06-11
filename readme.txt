
**RAIZ_DEL_PROYECTO**/
├── manage.py
├── Post
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── models.py
│   ├── pagination.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests
│   │   ├── test_Comments.py
│   │   ├── test_likes.py
│   │   └── test_Posts.py
│   ├── tests.py
│   └── viewSet.py
├── pytest.ini
├── requirements.txt
└── Users
    ├── admin.py
    ├── apps.py
    ├── __init__.py
    ├── models.py
    ├── serializers.py
    ├── tests
    │   └── test_user.py
    ├── tests.py
    └── viewSets.py


Usage
Registration and Authentication

    /register to sign up.

    /api-auth/login/ to log in.

Posts

    List: /Post

    Detail: /Post/id

    Create: /Post

To create a post, send a JSON with the following required fields:

    Title

    Content

    Is public

    Authenticated

    Team

Permissions are handled using a single number in the database ranging from 0 to 17, where 0 represents a private post and 17 is a public post with all possible access rights.
Authenticated users can never edit a post.
The values represent access levels as follows:

    0 means no access

    1 means read access

    2 means read and edit access

In the code, I handle permissions like this:
is_public * 9 + authenticated * 3 + team

The numbers are managed in base 3 (ternary numbers), where each digit represents a permission level related to the post, which will later be decoded to determine access.
This approach is used to save columns in the database and keep the application more optimized.

Likes

    List: /likes

    Filter: /likes/?post=i&user=id or separately

    Use GET and POST methods on the URL

Comments

    List: /comment

    Filter: /comment/?post=i&user=id or separately

    Use GET and POST methods on the URL

API Endpoints

{
  "register": "http://127.0.0.1:8000/register/",
  "registerTeams": "http://127.0.0.1:8000/registerTeams/",
  "Post": "http://127.0.0.1:8000/Post/",
  "comment": "http://127.0.0.1:8000/comment/",
  "likes": "http://127.0.0.1:8000/likes/"
}


Testing
Use pytest

