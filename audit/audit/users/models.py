from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import secrets


class UserManager(BaseUserManager):
    def create_user(self, eth_address, nonce=None):
        user = self.model(eth_address=eth_address, nonce=nonce or self.make_random_nonce())
        user.save(using=self._db)
        return user

    def make_random_nonce(self):
        import random
        return str(random.randint(100000, 999999))

class User(AbstractBaseUser):
    eth_address = models.CharField(max_length=42, unique=True)
    nonce = models.CharField(max_length=16, default="")

    USERNAME_FIELD = 'eth_address'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.eth_address
    
    def generate_nonce(self):
        self.nonce = secrets.token_hex(16)
        self.save()
