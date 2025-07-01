from enum import Enum

class Users(str, Enum):
    USERNAME = 'admin'
    PASSWORD = 'password123'

class Timeouts(float, Enum):
    TIMEOUT = 5.0