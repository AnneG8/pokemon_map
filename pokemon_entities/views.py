import folium

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Q

from pokemon_entities.models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def get_absolute_url(request, pokemon):
    img_url = DEFAULT_IMAGE_URL
    if pokemon.image:
        img_url = request.build_absolute_uri(pokemon.image.url)
    return img_url


def add_pokemon(folium_map, lat, lon, image_url):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def get_pokemon_map(request, pokemon_entitys):
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon_entitys:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            get_absolute_url(request, pokemon_entity.pokemon)
        )
    return folium_map


def get_pokemon_dict(request, pokemon):
    pokemon_dict = {
        'pokemon_id': pokemon.id,
        'img_url': get_absolute_url(request, pokemon),
        'title_ru': pokemon.title,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description
    }
    if pokemon.previous_evolution:
        pokemon_dict['previous_evolution'] = {
            'pokemon_id': pokemon.previous_evolution.id,
            'title_ru': pokemon.previous_evolution.title,
            'img_url': get_absolute_url(request, pokemon.previous_evolution),
        }
    next_evolutions = Pokemon.objects.filter(previous_evolution=pokemon)
    if next_evolutions:
        some_next_evolution = next_evolutions[0]
        pokemon_dict['next_evolution'] = {
            'pokemon_id': some_next_evolution.id,
            'title_ru': some_next_evolution.title,
            'img_url': get_absolute_url(request, some_next_evolution),
        }
    return pokemon_dict


def show_all_pokemons(request):
    q_filter = (Q(appeared_at__lte=timezone.localtime()) &
                Q(disappeared_at__gte=timezone.localtime()))

    pokemon_entitys = PokemonEntity.objects\
        .select_related('pokemon').filter(q_filter)
    folium_map = get_pokemon_map(request, pokemon_entitys)

    pokemon_types = Pokemon.objects.all()
    pokemons_on_page = []
    for pokemon in pokemon_types:
        pokemons_on_page.append(get_pokemon_dict(request, pokemon))

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    q_filter = (Q(appeared_at__lte=timezone.localtime()) &
                Q(disappeared_at__gte=timezone.localtime()))
    pokemon = get_object_or_404(Pokemon, id=int(pokemon_id))
    pokemon_entitys = pokemon.entities\
        .select_related('pokemon').filter(q_filter)

    folium_map = get_pokemon_map(request, pokemon_entitys)

    requested_pokemon = get_pokemon_dict(request, pokemon)

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': requested_pokemon
    })
