from dotenv import load_dotenv
import os
from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash, 
    get_flashed_messages, 
)
from user_repository import UserRepository
load_dotenv()
# Это callable WSGI-приложение

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

repo = UserRepository(app.config['DATABASE_URL'])


@app.route("/")
def hello_world():
    flash("Welcome to Flask!", "info")
    return redirect(url_for('users_get'), code=302)



@app.route("/users")
def users_get():
    messages = get_flashed_messages(with_categories=True)
    query = request.args.get('query', default='')
    users = repo.get_content()
    
    filtered_users = [user for user in users if query.lower() in (user.get('name') or '').lower()]
    return render_template(
        'users/index.html', 
        users=filtered_users, 
        search=query,
        messages=messages,
    )


@app.post('/users')
def users_post():
    user_data = request.form.to_dict()
    errors = validate(user_data)
    if errors:
        app.logger.error(f"Обнаружены ошибки валидации: {errors}")
        return render_template(
            "users/new.html",
            user=user_data,
            errors=errors,
        )
    repo.save(user_data)
    flash("User was added successfully", "success")
    return redirect(url_for('users_get'), code=302)


@app.route("/users/new")
def users_new():
    user = {"name": "", "email": ""}
    errors = {}
    return render_template(
        "users/new.html",
        user=user,
        errors=errors,
    )


@app.route("/users/<id>/edit")
def users_edit(id):
    user = repo.find(id)
    errors = {}

    return render_template(
        "users/edit.html",
        user=user,
        errors=errors,
    )


@app.route("/users/<id>/update", methods=["POST"])
def users_update(id):
    user = repo.find(id)
    if user is None:
        return "User not found", 404
    user_data = request.form.to_dict()
    errors = validate(user_data, is_update=True)
    if errors:
        return render_template(
            "users/edit.html",
            user=user_data,
            errors=errors,
        ), 422
    user_data['id'] = user['id']
    repo.save(user_data)
    flash("User was updated successfully", "success")
    return redirect(url_for('users_get'), code=302)



@app.route("/users/<id>/delete", methods=["POST"])
def users_delete(id):
    repo.destroy(id)
    flash("User has been deleted", "success")
    return redirect(url_for("users_get"), code=303)


@app.route('/users/<id>')
def users_show(id):
    user = repo.find(id)
    return render_template('/users/show.html',
                           user=user)


def validate(user, is_update=False):
    errors = {}
    if not is_update and not user["name"]:
        errors["name"] = "Can't be blank"
    if not is_update and not user["email"]:
        errors["email"] = "Can't be blank"

    return errors