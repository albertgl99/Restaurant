from django.http import HttpResponse, HttpResponseRedirect
from .mongo import afegir_plat, obtenir_tots_els_plats, get_database
from django.shortcuts import render, redirect
from django.contrib import messages
import bcrypt
from bson.objectid import ObjectId
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import random
import re  

def home(request):
    user_info = {}
    if 'user_id' in request.session:
        db = get_database()
        users_collection = db['Usuaris']
        user_id = request.session['user_id']
        # Assegura't d'importar ObjectId de bson per a convertir l'string a ObjectId
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user_info = {'nom': user['nom'], 'email': user['email']}

    return render(request, 'home.html', {'user_info': user_info})

def view_afegir_plat(request):
    if request.method == "POST":
        nom = request.POST.get('name')
        categoria = request.POST.get('category')  
        preu = request.POST.get('price')
        descripcio = request.POST.get('description')  
        
        nou_plat = {
            "nom": nom,
            "categoria": categoria,
            "preu": float(preu),
            "descripcio": descripcio,
        }
        
        # Utilitza la funció afegir_plat per emmagatzemar el nou plat a la base de dades
        afegir_plat(nou_plat)
        
        return redirect('llista_plats')
    else:
        # Si no és una petició POST, simplement mostra el formulari
        return render(request, "crear_plat.html")


def llista_plats(request):
    db = get_database()
    col = db['Plats']
    # Recupera els plats agrupats per categoria
    primers = list(col.find({'categoria': 'Primer'}))
    segons = list(col.find({'categoria': 'Segon'}))
    postres = list(col.find({'categoria': 'Postre'}))

    # Converteix ObjectId a string per a cada plat
    for categoria in (primers, segons, postres):
        for plat in categoria:
            plat['id'] = str(plat['_id'])

    return render(request, 'llista_plats.html', {
        'primers': primers,
        'segons': segons,
        'postres': postres
    })


def register(request):
    context = {'errors': {}, 'data': request.POST}
    if request.method == 'POST':
        db = get_database()
        users_collection = db['Usuaris']

        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm-password', '')

        # Validacions
        if not username.isalpha():
            context['errors']['username'] = 'El nom d\'usuari ha de contenir només lletres.'

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            context['errors']['email'] = 'Introdueix un correu electrònic vàlid.'

        if len(password) < 8:
            context['errors']['password'] = 'La contrasenya ha de tenir almenys 8 caràcters.'

        if password != confirm_password:
            context['errors']['confirm_password'] = 'Les contrasenyes no coincideixen.'

        if users_collection.find_one({"email": email}):
            context['errors']['email'] = 'L\'email ja està en ús.'

        if not context['errors']:  # Si no hi ha errors, procedim a registrar l'usuari
            hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            new_user = {
                "nom": username,
                "email": email,
                "rol": "client",
                "pwd": hashed_pwd,
            }
            users_collection.insert_one(new_user)
            messages.success(request, 'Usuari registrat amb èxit.')
            return redirect('login')

    return render(request, 'register.html', context)



def login(request):
    if request.method == 'POST':
        # Assumim que get_database() està definit i retorna la teva connexió a MongoDB
        db = get_database()
        users_collection = db['Usuaris']

        username = request.POST.get('username')
        password = request.POST.get('password').encode('utf-8')  # Assegura't que la contrasenya està en bytes

        user = users_collection.find_one({"nom": username})
        
        # Comprova si l'usuari existeix i la contrasenya és correcta
        if user and bcrypt.checkpw(password, user['pwd']):
            # Suposem que 'email' és un camp disponible en l'objecte 'user'
            user_email = user['email']  # Obté el correu electrònic de l'usuari
            
            # Emmagatzema l'ID de l'usuari a la sessió
            request.session['user_id'] = str(user['_id'])
            
            return redirect('home')  # Redirigeix a la pàgina d'inici o una altra pàgina de la teva elecció
        else:
            messages.error(request, 'Usuari o contrasenya incorrectes')

    # Si el mètode és GET o l'autenticació falla, mostra el formulari de login
    return render(request, 'login.html')

def logout(request):
    # Elimina l'ID de l'usuari de la sessió per "desconnectar" l'usuari
    if 'user_id' in request.session:
        del request.session['user_id']
        request.session.flush()  # Opcional: Elimina totes les dades de la sessió
    
    messages.success(request, 'Has tancat la sessió amb èxit.')
    
    # Redirigeix a la pàgina d'inici o a la pàgina de login
    return redirect('home')


def eliminar_plat(request, plat_id):
    if request.method == 'POST':
        db = get_database()
        plats_collection = db.Plats
        
        # Eliminar el plat
        plats_collection.delete_one({'_id': ObjectId(plat_id)})
        
        # Mostrar missatge d'èxit
        messages.success(request, 'Plat eliminat amb èxit.')
        
        # Redirigir a la llista de plats
        return redirect('llista_plats')
    
def modificar_plat(request, plat_id):
    db = get_database()
    plats_collection = db['Plats']
    plat = plats_collection.find_one({"_id": ObjectId(plat_id)})

    if request.method == 'POST':
        # Actualitza el plat basat en les dades del formulari
        updated_data = {
            "nom": request.POST.get('name'),
            "categoria": request.POST.get('category'),
            "preu": float(request.POST.get('price')),
            "descripcio": request.POST.get('description'),
        }
        plats_collection.update_one({'_id': ObjectId(plat_id)}, {'$set': updated_data})
        messages.success(request, 'Plat modificat amb èxit')
        return redirect('llista_plats')
    else:
        # Passa les dades del plat al formulari per editar
        context = {'plat': plat, 'plat_id': plat_id}
        return render(request, 'crear_plat.html', context)

def seleccionar_carta_setmanal(request):
    db = get_database()
    col = db['Plats']
    primers = list(col.find({'categoria': 'Primer'}))
    segons = list(col.find({'categoria': 'Segon'}))
    postres = list(col.find({'categoria': 'Postre'}))
    plats = primers + segons + postres

    for plat in plats:
        plat['id'] = str(plat['_id'])

    if request.method == 'POST':
        plats_seleccionats = request.POST.getlist('plats_seleccionats')
        request.session['plats_seleccionats'] = plats_seleccionats  # Guarda a la sessió
        return redirect('mostra_carta_setmanal')

    context = {
        'primers': primers,
        'segons': segons,
        'postres': postres,
        'plats_seleccionats': request.session.get('plats_seleccionats', [])
    }

    return render(request, 'seleccionar_carta_setmanal.html', context)


def mostra_carta_setmanal(request):
    db = get_database()
    plats_collection = db['Plats']
    plats_seleccionats = request.session.get('plats_seleccionats', [])

    primers = list(plats_collection.find({'_id': {'$in': [ObjectId(id) for id in plats_seleccionats]}, 'categoria': 'Primer'}))
    segons = list(plats_collection.find({'_id': {'$in': [ObjectId(id) for id in plats_seleccionats]}, 'categoria': 'Segon'}))
    postres = list(plats_collection.find({'_id': {'$in': [ObjectId(id) for id in plats_seleccionats]}, 'categoria': 'Postre'}))

    context = {
        'primers': primers,
        'segons': segons,
        'postres': postres
    }

    return render(request, 'mostra_carta_setmanal.html', context)






def carta_aleatoria(request):
    db = get_database()
    plats_collection = db['Plats']
    
    # Obté els plats per categoria
    primers = list(plats_collection.find({"categoria": "Primer"}))
    segons = list(plats_collection.find({"categoria": "Segon"}))
    postres = list(plats_collection.find({"categoria": "Postre"}))

    # Selecciona 3 plats aleatòriament de cada categoria, o menys si no hi ha suficients plats
    num_primers = min(len(primers), 3)
    num_segons = min(len(segons), 3)
    num_postres = min(len(postres), 3)

    primers_aleatoris = random.sample(primers, num_primers) if num_primers > 0 else []
    segons_aleatoris = random.sample(segons, num_segons) if num_segons > 0 else []
    postres_aleatoris = random.sample(postres, num_postres) if num_postres > 0 else []

    context = {
        'primers': primers_aleatoris,
        'segons': segons_aleatoris,
        'postres': postres_aleatoris,
    }

    return render(request, 'carta_aleatoria.html', context)

