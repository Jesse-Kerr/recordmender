

app = Flask(__name__)

 

@app.route('/login')
def login():
    return 'login'

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User {}'.format(username)

with app.test_request_context():
    print(url_for('home_page'))
    print(url_for('login'))
    print(url_for('login', next='/'))
    print(url_for('show_user_profile', username='John Doe'))

# @app.route('/post/<int:post_id>')
# def show_post(post_id):
#     # show the post with the given id, the id is an integer
#     return 'Post {}'.format(post_id)

# @app.route('/path/<path:subpath>')
# def show_subpath(subpath):
#     # show the subpath after /path/
#     return 'Subpath %s' % subpath
# @app.route('/hello')
# def hello():
#     return 'Hello, World'

if __name__ == "__main__":
    app.run()