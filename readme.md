
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

    2 means read and edit post access

An author always has full permissions on their post.

In the code, permissions are handled like this:
is_public * 9 + authenticated * 3 + team

The numbers are managed in base 3 (ternary numbers), where each digit represents a permission level related to the post, which will later be decoded to determine access.
This approach is used to save columns in the database and keep the application more optimized.

Likes and comments are also based on these permissions. If a user can read a post, they can like or comment on it. However, if the user is not authenticated, they won’t be able to like or comment on any post
***
***Likes***

    List: /likes
        
    Filter: /likes/?post=i&user=id or separately

    Use GET and POST methods on the URL

***
***Comments***

    List: /comment

    Filter: /comment/?post=i&user=id or separately

    Use GET and POST methods on the URL

    A comment can´t be updated after posting it but it can by deleted by its author
    

You can also retrieve the details of a like or comment by passing its ID as a URL parameter

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

