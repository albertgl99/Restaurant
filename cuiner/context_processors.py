from django.contrib.auth import get_user_model
from .mongo import get_database
from bson.objectid import ObjectId

def user_info(request):
    user_details = {}
    if 'user_id' in request.session:
        db = get_database()
        users_collection = db['Usuaris']
        user_id = request.session['user_id']
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user_details = {'nom': user['nom'], 'email': user['email']}
    return {'user_info': user_details}
