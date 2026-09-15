import re
from django.core.exceptions import ValidationError

def username_validation(username):
    if not re.match(r'^[a-zA-Z0-9_]+$',username):
        raise ValidationError('Username only contains letters(a-z,A-Z),numbers(0-9) and underscores(_)')