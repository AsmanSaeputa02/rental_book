# 🔧 user/functions/user.py
from user.models import User

class UserService:
    @staticmethod
    def list_users():
        return User.objects.all()
    

    @staticmethod
    def get_user(user_id:int):
        return User.objects.get(id=user_id)
    
    @staticmethod
    def create_user(data:dict) -> User:
        password = data.pop("password")
        user = User.objects.create(**data)
        user.set_password(password)
        user.save()
        return user
    
    @staticmethod
    def update_user(user_id:int , data:dict)-> User:
        user = User.objects.get(id=user_id)
        if "password" in data:
            password = data.pop("password")
            user.set_password(password)
        for key , value in data.pop("password"):
            setattr(user , key , value)
        user.save()
        return user
    
    @staticmethod
    def delete_user(user_id:int):
        user  = User.objects.get(id=user_id)
        user.adelete()