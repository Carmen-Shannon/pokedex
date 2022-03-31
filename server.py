from flask_app import app
from flask import redirect, render_template, session
from flask_app.models.user import User
from flask_app.models import pokemon
from flask_app.controllers import users, main


@app.route('/', methods=['POST', 'GET'])
async def index():
    try:
        data = {'id': session['current_id']}
        current_user = User.get_user_by_id(data)
        pokemon_in_pc = pokemon.Pokemon.get_pokemon_by_user(data)
        to_show = []
        if not pokemon_in_pc:
            return render_template('index.html', user=current_user, pokemon=False)
        for p in range(len(pokemon_in_pc)):
            sprite = await pokemon.get_pokemon_info(pokemon_in_pc[p].national_id)
            sprite = sprite['sprites']['front_default']
            to_show.append(sprite)
        return render_template('index.html', user=current_user, sprites=to_show, pokemon=pokemon_in_pc)
    except KeyError:
        return render_template('index.html', user=False)


@app.route('/about_page')
def render_about_page():
    try:
        if session['current_id']:
            return render_template('about.html', user=True)
    except KeyError:
        return render_template('about.html', user=False)


@app.route('/home')
def home():
    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
