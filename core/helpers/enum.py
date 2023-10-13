"""

    This file will contain only functions or class for Enum in whole project.

"""
from enum import Enum


class LoginEnum(Enum):
    ACTIVATION_IN_PROGRESS = {
        "en": "Please provide post data with email and password",
        "hr": "Molimo upišite email adresu i lozinku."
    }

    NO_CONTENT = {
        "en": "Please provide post data with email and password",
        "hr": "Molimo upišite email adresu i lozinku."
    }

    USER_DEACTIVATED = {
        "en": "Your account is disabled.",
        "hr": "Vaš korisnički račun je onemogućen."
    }

    USER_NOT_FOUND = {
        "en": "User not found with provided credentials.",
        "hr": "Nije pronađen korisnik s navedenim podacima."
    }

    USER_MODULES_NOT_FOUND = {
        "en": "User modules not found with provided credentials.",
        "hr": "Nije pronađen korisnički modul s navedenim podacima."
    }

    USER_NOT_CONFIRMED = {
        "en": "User not confirmed, please check your email for confirmation.",
        "hr": "Korisnik nije potvrdio svoj račun, molimo provjerite svoj email."
    }

    USER_SUCCESS = {
        "en": "User successfully logged in.",
        "hr": "Korisnik se uspješno prijavio."
    }

    USER_STEP_REQ = {
        "en": "Please finish registration flow.",
        "hr": "Molimo završite registriranje korisnika."
    }

    USER_NOT_ON_CLUSTER = {
        "en": "User has no assigned clusters. Please contact your site administrator to proceed.",
        "hr": "Korisnik nije dodijeljen na podružnicu. Molimo kontaktirajte svojeg administratora za nastavak."
    }

    USER_NO_PERMISSIONS = {
        "en": "User has no permissions. Please contact your site administrator to proceed.",
        "hr": "Korisnik nema dodijeljenih dopuštenja. Molimo kontaktirajte svojeg administratora za nastavak."
    }


class ActivateToken(Enum):
    USER_NOT_FOUND = {
        "en": "User not found with provided credentials.",
        "hr": "Nije pronađen korisnik s navedenim podacima."
    }

    USER_ACTIVATED = {
        "en": "User is activated.",
        "hr": "Korisnički račun je aktiviran."
    }

    USER_ACTIVATE_PASSWORD = {
        "en": "User successfully updated. Check your email for password reset link.",
        "hr": "Korisnički račun je uspješno ažuriran. Provjerite svoj email za poveznicu za resetiranje lozinke."
    }

    USER_CHANGE_PASSWORD = {
        "en": "User password successfully updated.",
        "hr": "Korisnička lozinka je uspješno ažurirana."
    }

    USER_DATA_PASSWORD = {
        "en": "Please provide password.",
        "hr": "Molimo unesite lozinku."
    }


class RegisterEnum(Enum):
    EMAIL_EXISTS = {
        "en": "User with email already exists.",
        "hr": "Korisnik s navedenom email adresom već postoji."
    }
    EMAIL_NOT_FOUND_IN_POST_DATA_EXISTS = {
        "en": "Please provide all post data fields.",
        "hr": "Molimo unesite podatke u sva polja."
    }
    USER_SUCCESS = {
        "en": "User successfully created. Check your email for activation code.",
        "hr": "Korisnički račun je uspješno kreiran. Aktivacijski kod je poslan na vašu email adresu."
    }


class GlobalRestEnum(Enum):
    NOT_FOUND_404 = {
        "en": "There is no data.",
        "hr": "Nema podataka."
    }

    FORBIDDEN_403 = {
        "en": "Request forbidden.",
        "hr": "Zabranjen pristup."
    }

    FORBIDDEN_400 = {
        "en": "Bad request.",
        "hr": "Krivi unos podataka."
    }

    SUCCESS_200 = {
        "en": "Success request.",
        "hr": "Uspješni unos podataka."
    }

    SUCCESS_201 = {
        "en": "Success validated and saved.",
        "hr": "Unos podataka uspješan i pospremljen."
    }
