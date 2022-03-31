import requests
from flask_app.config.mysqlconnection import connectToMySQL as connect


async def get_pokemon_info(user_input):
    url = f'https://pokeapi.co/api/v2/pokemon/{user_input}'
    pokemon_info = requests.get(url)
    return pokemon_info.json()


async def get_pokemon_species(user_input):
    url = await get_pokemon_info(user_input)
    url = url['species']['url']
    species = requests.get(url)
    return species.json()


async def get_ability(id):
    ability = requests.get(id)
    return ability.json()


async def capitalize_name(user_input):
    name = await get_pokemon_info(user_input)
    name = name['name']
    return name[0].upper() + name[1:]


async def get_types(user_input):
    types_dict = await get_pokemon_info(user_input)
    types_dict = types_dict['types']
    types = ''
    for t in range(len(types_dict)):
        if len(types_dict) == 1:
            types = types_dict[t]['type']['name']
        else:
            if t == 0:
                types += types_dict[t]['type']['name'] + ', '
            else:
                types += types_dict[t]['type']['name']
    return types


async def convert_height_to(user_input, measurement):
    pokemon = await get_pokemon_info(user_input)
    pokemon = pokemon['height']

    if measurement == 'cm':
        return pokemon * 10
    if measurement == 'in':
        return round((pokemon * 10) * 0.3937008)
    if measurement == 'm':
        return round((pokemon * 10) * 0.01, 2)
    if measurement == 'ft':
        return round(((pokemon * 10) * 0.3937008) * 0.08333333, 2)


async def get_abilities(user_input):
    abilities_dict = await get_pokemon_info(user_input)
    abilities_dict = abilities_dict['abilities']
    abilities = []
    for a in range(len(abilities_dict)):
        if len(abilities_dict) == 1:
            abilities.append(abilities_dict[a]['ability']['name'])
        else:
            abilities.append(abilities_dict[a]['ability']['name'])

    return abilities


async def get_ability_values(user_input):
    abilities = await get_pokemon_info(user_input)
    abilities = abilities['abilities']
    ability_urls = []

    for a in range(len(abilities)):
        ability_urls.append(abilities[a]['ability']['url'])

    ability_effects = []

    for x in range(len(ability_urls)):
        effect = await get_ability(ability_urls[x])
        effect = effect['effect_entries'][1]['effect']
        ability_effects.append(effect)

    return ability_effects


async def get_stats(user_input, var):
    stats_dict = await get_pokemon_info(user_input)
    stats_dict = stats_dict['stats']
    stats = []
    if var == 'name':
        for s in range(len(stats_dict)):
            stats.append(
                str(stats_dict[s]['stat']['name'])
            )
        return stats
    if var == 'stats':
        for s in range(len(stats_dict)):
            stats.append(
                stats_dict[s]['base_stat']
            )
        return stats

 
async def get_evolution_chain(user_input):
    pokemon = await get_pokemon_species(user_input)
    pokemon = pokemon['evolution_chain']['url']
    evolution_chain = requests.get(pokemon)
    evolution_chain = evolution_chain.json()
    evolution_chain = evolution_chain['chain']
    evo_list = []
    toggle = True
    while toggle:
        try:
            sprite = await get_pokemon_info(evolution_chain['species']['name'])
            sprite = sprite['sprites']['front_default']
            evo_list.append(sprite)
            evolution_chain = evolution_chain['evolves_to'][0]
        except IndexError:
            toggle = False

    return evo_list


class Pokemon:
    def __init__(self, data):
        self.id = data['id']
        self.user_id = data['user_id']
        self.name = data['name']
        self.national_id = data['national_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def get_pokemon_by_user(cls, data):
        query = 'SELECT * FROM pokemon WHERE user_id = %(id)s;'
        results = connect('pokedex_db').query_db(query, data)
        pokemon_in_pc = []

        if results == False or len(results) < 1:
            return False

        for pokemon in results:
            pokemon_in_pc.append(cls(pokemon))

        return pokemon_in_pc

    @classmethod
    def check_dup(cls, data):
        query = 'SELECT * FROM pokemon WHERE user_id = %(user_id)s AND national_id = %(national_id)s;'
        result = connect('pokedex_db').query_db(query, data)

        if not result:
            return False
        else:
            return True

    @classmethod
    def check_pc_size(cls, data):
        query = 'SELECT * FROM pokemon WHERE user_id = %(id)s;'
        results = connect('pokedex_db').query_db(query, data)

        if len(results) > 8:
            return False

        return True
