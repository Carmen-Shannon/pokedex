from flask_app import app
from flask_app.models import user
from flask_app.models.pokemon import *
from flask import redirect, session, render_template, request, flash
import requests
import json


@app.route('/search_pokemon', methods=['POST', 'GET'])
async def pokemon():

    try:
        if session['current_id']:
            data = {'id': session['current_id']}
            current_user = user.User.get_user_by_id(data)
    except KeyError:
        current_user = False

    search_result = request.form['searchbar']

    if search_result.isalpha() or search_result.isnumeric():

        try:

            if search_result.isalpha():
                search_result = search_result.lower()

            # Gets main json dump of pokemon
            pokemon_info = await get_pokemon_info(search_result)

            # Gets species branch
            species = await get_pokemon_species(search_result)

            # Capitalize first letter of name for good looks
            poke_name = await capitalize_name(search_result)

            # Get all types for pokemon
            types = await get_types(search_result)

            # Converts height/weight to different measurements
            poke_height_cm = await convert_height_to(search_result, 'cm')
            poke_height_in = await convert_height_to(search_result, 'in')
            poke_height_m = await convert_height_to(search_result, 'm')
            poke_height_ft = await convert_height_to(search_result, 'ft')
            poke_weight_lb = await convert_weight_to(search_result, 'lb')

            # Gets all abilities
            abilities = await get_abilities(search_result)

            # Get names of stats and data in order for graph.js
            stats_names = await get_stats(search_result, 'name')
            base_stats = await get_stats(search_result, 'stats')
            stats_names = json.dumps(stats_names)
            base_stats = json.dumps(base_stats)

            # Check if pokemon is in pc otherwise set false
            try:
                if session['current_id']:
                    data = {
                        'user_id': session['current_id'],
                        'national_id': pokemon_info['id']
                    }
                    is_in_pc = Pokemon.check_dup(data)
            except KeyError:
                is_in_pc = False

            # Check if user has too many pokemon otherwise set false
            try:
                if session['current_id']:
                    data2 = {'id': session['current_id']}
                    has_too_many = Pokemon.check_pc_size(data2)
            except KeyError:
                has_too_many = False

            # Get effects from abilities for hover description
            ability_effects = await get_ability_values(pokemon_info['id'])

            # Get evolution chain as list of urls pointing to sprite art
            evolution_chain = await get_evolution_chain(pokemon_info['id'])

            # Get move list
            moves = await get_move_list(pokemon_info['id'])

            return render_template('pokemon_info.html', pokemon=pokemon_info, species=species, poke_name=poke_name, types=types, poke_height_cm=poke_height_cm, poke_height_in=poke_height_in, abilities=abilities, user=current_user, stats_names=stats_names, base_stats=base_stats, poke_height_m=poke_height_m, poke_height_ft=poke_height_ft, is_in_pc=is_in_pc, pc_size=has_too_many, effects=ability_effects, evolution_chain=evolution_chain, weight=poke_weight_lb, moves=moves)

        except requests.exceptions.JSONDecodeError:

            flash('Please check your spelling and try again', 'main')
            return redirect('/')

    else:
        flash('Please enter a name of a pokemon or national id', 'main')
        return redirect('/')


@app.route('/add_to_pc/<int:id>', methods=['POST', 'GET'])
async def add_to_pc(id):
    try:
        if session['current_id']:
            data2 = {
                'user_id': session['current_id'],
                'national_id': id
            }
            data = {'id': session['current_id']}
            if not Pokemon.check_dup(data2) and Pokemon.check_pc_size(data):
                name = await get_pokemon_info(id)
                name = name['name']
                data3 = {
                    'user_id': session['current_id'],
                    'name': name,
                    'national_id': id
                }
                user.User.add_to_pc(data3)
            return redirect('/')
    except KeyError:
        return redirect('/')


@app.route('/remove_from_pc/<int:id>', methods=['POST', 'GET'])
async def remove_from_pc(id):
    try:
        if session['current_id']:
            data = {'id': session['current_id'], 'national_id': id}
            user.User.remove_from_pc(data)
            return redirect('/')
    except KeyError:
        return redirect('/')


@app.route('/clear_pc', methods=['POST', 'GET'])
async def clear_pc():
    try:
        if session['current_id']:
            data = {'id': session['current_id']}
            user.User.clear_pc(data)
            return redirect('/')
    except KeyError:
        return redirect('/')


@app.route('/search_pokemon/<int:id>', methods=['POST', 'GET'])
async def pokemon_from_pc(id):

    try:
        if session['current_id']:
            data = {'id': session['current_id']}
            current_user = user.User.get_user_by_id(data)
    except KeyError:
        current_user = False

    search_result = id

    # Gets main json dump of pokemon
    pokemon_info = await get_pokemon_info(search_result)

    # Gets species branch
    species = await get_pokemon_species(search_result)

    # Capitalize first letter of name for good looks
    poke_name = await capitalize_name(search_result)

    # Get all types for pokemon
    types = await get_types(search_result)

    # Converts height to different measurements
    poke_height_cm = await convert_height_to(search_result, 'cm')
    poke_height_in = await convert_height_to(search_result, 'in')
    poke_height_m = await convert_height_to(search_result, 'm')
    poke_height_ft = await convert_height_to(search_result, 'ft')
    poke_weight_lb = await convert_weight_to(search_result, 'lb')

    # Gets all abilities
    abilities = await get_abilities(search_result)

    # Get names of stats and data in order for graph.js
    stats_names = await get_stats(search_result, 'name')
    base_stats = await get_stats(search_result, 'stats')
    stats_names = json.dumps(stats_names)
    base_stats = json.dumps(base_stats)

    # Check if pokemon is in pc to add/delete
    data = {
        'user_id': session['current_id'],
        'national_id': pokemon_info['id']
    }
    is_in_pc = Pokemon.check_dup(data)

    # Check if user has too many pokemon
    data2 = {'id': session['current_id']}
    has_too_many = Pokemon.check_pc_size(data2)

    # Get effects from abilities for hover description
    ability_effects = await get_ability_values(pokemon_info['id'])

    # Get evolution chain as list of urls pointing to sprite art
    evolution_chain = await get_evolution_chain(pokemon_info['id'])

    # Get move list
    moves = await get_move_list(pokemon_info['id'])

    return render_template('pokemon_info.html', pokemon=pokemon_info, species=species, poke_name=poke_name, types=types, poke_height_cm=poke_height_cm, poke_height_in=poke_height_in, abilities=abilities, user=current_user, stats_names=stats_names, base_stats=base_stats, poke_height_m=poke_height_m, poke_height_ft=poke_height_ft, is_in_pc=is_in_pc, pc_size=has_too_many, effects=ability_effects, evolution_chain=evolution_chain, weight=poke_weight_lb, moves=moves)
