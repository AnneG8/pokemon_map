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


def get_pokemon_entitys(pokemon_id=None):
    timezone.activate('Europe/Moscow')
    q_filter = (Q(appeared_at__lte=timezone.localtime(timezone.now())) &
                Q(disappeared_at__gte=timezone.localtime(timezone.now())))
    if pokemon_id:
        q_filter = q_filter & Q(pokemon__id=int(pokemon_id))

    pokemon_entitys = PokemonEntity.objects\
        .select_related('pokemon').filter(q_filter)
    return pokemon_entitys


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


def get_pokemon_map(request, pokemon_id=None):
    pokemon_entitys = get_pokemon_entitys(pokemon_id)
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon_entitys:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            get_absolute_url(request, pokemon_entity.pokemon)
        )
    return folium_map


def get_pokemon_dict(request, pokemon):
    return {
        'pokemon_id': pokemon.id,
        'img_url': get_absolute_url(request, pokemon),
        'title_ru': pokemon.title,
        'title_en': '',
        'title_jp': '',
        'description': '',
        'next_evolution': '',
        'previous_evolution': ''
    }


def show_all_pokemons(request):
    folium_map = get_pokemon_map(request)

    pokemon_types = Pokemon.objects.all()
    pokemons_on_page = []
    for pokemon in pokemon_types:
        pokemons_on_page.append(get_pokemon_dict(request, pokemon))

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    folium_map = get_pokemon_map(request, pokemon_id)

    pokemon = get_object_or_404(Pokemon, id=int(pokemon_id))
    requested_pokemon = get_pokemon_dict(request, pokemon)

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': requested_pokemon
    })
