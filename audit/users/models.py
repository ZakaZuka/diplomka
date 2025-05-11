from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, eth_address):
        user = self.model(eth_address=eth_address.lower())
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    eth_address = models.CharField(max_length=42, unique=True)
    nonce = models.CharField(max_length=255)
    
    USERNAME_FIELD = 'eth_address'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.eth_address
