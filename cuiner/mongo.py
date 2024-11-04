from pymongo import MongoClient

def get_database():
    # Connexió URI
    CONNECTION_STRING = "mongodb://localhost:27017"
    
    # Crea una connexió utilitzant MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Crea la base de dades 'django_project'
    return client['Restaurant']
    
def afegir_plat(plat):
    db = get_database()  # Assegura't que aquesta funció també està definida i accessible
    col = db.Plats
    resultat = col.insert_one(plat)
    return resultat.inserted_id

def obtenir_tots_els_plats():
    db = get_database()
    col = db.Plats
    plats = col.find()
    return list(plats) 
