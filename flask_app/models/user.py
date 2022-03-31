from flask import flash, request
from flask_app.config.mysqlconnection import connectToMySQL as connect
import re
from flask_bcrypt import Bcrypt
from flask_app import app
from flask_app.models import pokemon
bcrypt = Bcrypt(app)


class User:
    def __init__(self, data):
        self.id = data['id']
        self.username = data['username']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.pokemon_in_pc = []

    @staticmethod
    def validate_reg(user):
        is_valid = True
        data = {'email': user['email']}
        data2 = {'username': user['username']}
        email_exists = User.get_user_by_email(data)
        username_exists = User.get_user_by_username(data2)
        special_characters = ['"', '!', '@', '#', '$', '%', '^', '&', '*',
                              '(', ')', '-', '=', '+', '<', '>', '.', ',', '/', '?', '`', '~', ' ', "'"]
        EMAIL_REGEX = re.compile(
            r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if len(user['username']) < 3 or user['username'] == '' or any(char in special_characters for char in user['username']):
            flash(
                'Username must be at least 3 characters and can not contain special characters or spaces', 'reg')
            is_valid = False
        if not EMAIL_REGEX.match(user['email']) or user['email'] == '':
            flash('Invalid email', 'reg')
            is_valid = False
        if email_exists:
            flash('Email already exists', 'reg')
            is_valid = False
        if username_exists:
            flash('Username already exists', 'reg')
            is_valid = False
        if user['password'] != user['confirm_password']:
            flash('Passwords do not match', 'reg')
            is_valid = False
        if len(user['password']) < 8 or user['password'] == '' or user['password'].isalpha():
            flash(
                'Passwords must be at least 8 characters and contain a number or special character', 'reg')
        return is_valid

    @staticmethod
    def validate_login(user):
        is_valid = True
        data = {'username': user['username']}
        username_exists = User.get_user_by_username(data)
        if not username_exists:
            flash('Username does not exist', 'login')
            is_valid = False
        if not request.form['password'] or not bcrypt.check_password_hash(username_exists.password, request.form['password']):
            flash('Invalid email/password', 'login')
            is_valid = False
        return is_valid

    @classmethod
    def add_user(cls, data):
        query = 'INSERT INTO users (username, email, password, created_at, updated_at) VALUES (%(username)s, %(email)s, %(password)s, NOW(), NOW());'
        return connect('pokedex_db').query_db(query, data)

    @classmethod
    def get_user_by_id(cls, data):
        query = 'SELECT * FROM users WHERE id = %(id)s;'
        result = connect('pokedex_db').query_db(query, data)

        if result == False or len(result) < 1:
            return False

        return cls(result[0])

    @classmethod
    def get_user_by_email(cls, data):
        query = 'SELECT * FROM users WHERE email = %(email)s;'
        result = connect('pokedex_db').query_db(query, data)

        if result == False or len(result) < 1:
            return False

        return cls(result[0])

    @classmethod
    def get_user_by_username(cls, data):
        query = 'SELECT * FROM users WHERE username = %(username)s;'
        result = connect('pokedex_db').query_db(query, data)

        if result == False or len(result) < 1:
            return False

        return cls(result[0])

    @classmethod
    def add_to_pc(cls, data):
        query = 'INSERT INTO pokemon (user_id, name, national_id, created_at, updated_at) VALUES (%(user_id)s, %(name)s, %(national_id)s, NOW(), NOW());'
        return connect('pokedex_db').query_db(query, data)
    
    @classmethod
    def remove_from_pc(cls, data):
        query = 'DELETE FROM pokemon WHERE user_id = %(id)s AND national_id = %(national_id)s;'
        return connect('pokedex_db').query_db(query, data)
    
    @classmethod
    def clear_pc(cls, data):
        query = 'DELETE FROM pokemon WHERE user_id = %(id)s;'
        return connect('pokedex_db').query_db(query, data)
