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


class PositionLabelSuffix(Enum):
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4
    F = 5
    G = 6
    H = 7
    I = 8
    J = 9
    K = 10
    L = 11
    M = 12
    N = 13
    O = 14
    P = 15
    Q = 16
    R = 17
    S = 18
    T = 19
    U = 20
    V = 21
    W = 22
    X = 23
    Y = 24
    Z = 25
    AA = 26
    AB = 27
    AC = 28
    AD = 29
    AE = 30
    AF = 31
    AG = 32
    AH = 33
    AI = 34
    AJ = 35
    AK = 36
    AL = 37
    AM = 38
    AN = 39
    AO = 40
    AP = 41
    AQ = 42
    AR = 43
    AS = 44
    AT = 45
    AU = 46
    AV = 47
    AW = 48
    AX = 49
    AY = 50
    AZ = 51
    BA = 52
    BB = 53
    BC = 54
    BD = 55
    BE = 56
    BF = 57
    BG = 58
    BH = 59
    BI = 60
    BJ = 61
    BK = 62
    BL = 63
    BM = 64
    BN = 65
    BO = 66
    BP = 67
    BQ = 68
    BR = 69
    BS = 70
    BT = 71
    BU = 72
    BV = 73
    BW = 74
    BX = 75
    BY = 76
    BZ = 77
    CA = 78
    CB = 79
    CC = 80
    CD = 81
    CE = 82
    CF = 83
    CG = 84
    CH = 85
    CI = 86
    CJ = 87
    CK = 88
    CL = 89
    CM = 90
    CN = 91
    CO = 92
    CP = 93
    CQ = 94
    CR = 95
    CS = 96
    CT = 97
    CU = 98
    CV = 99
    CW = 100
    CX = 101
    CY = 102
    CZ = 103