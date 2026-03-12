from functools import wraps
from flask_login import current_user, login_required
from flask import abort

def professor_required(f):
    @wraps(f)
    @login_required # Garante que o usuário está logado, se não redireciona pra login
    def wrapper(*args, **kwargs): #Sei o que é isso de *args e **kwargs não, mas vi que é normal usar isso e tô usando
        if current_user.usr_tipo != "professor":
            abort(403)
        return f(*args, **kwargs)
    return wrapper
