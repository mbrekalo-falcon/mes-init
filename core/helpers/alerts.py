import hashlib
import re
from django.core.cache import cache
from models.cluster.models import ClusterRoleAlert


SYSTEM_ALERT_MESSAGES = {
    1000: {
        "note": "SYSTEM DOWNTIME, targets all userst",
        "alert_type_id": 3,
        "application_role_id": None,
        "data": {
            "en": "%__date at %__time system changes will take effect "
                  "and application will be unavailable for %__downtime %__dt_unit.",
            "hr": "%__date u %__time provodit će se izmjene na sustavu "
                  "i aplikacija neće biti dostupna %__downtime %__dt_unit."
        }
    },
    1001: {
        "note": "SYSTEM CHANGES, targets all users",
        "alert_type_id": 3,
        "application_role_id": None,
        "data": {
            "en": "Changes in the application have been applied, refresh the screen within the application (CTRL+F5).",
            "hr": "Izmjene na aplikaciji su primijenjene, molimo osvježite ekran unutar aplikacije (CTRL+F5)."
        }
    },
}


class SystemAlertMessage(object):
    def __init__(self, message_type, cluster_id=None, user_id=None):
        self.message_type = message_type
        self.cluster_id = cluster_id
        self.alert_type_id = SYSTEM_ALERT_MESSAGES[message_type]["alert_type_id"]
        self.application_role_id = SYSTEM_ALERT_MESSAGES[message_type]["application_role_id"]
        self.user_id = user_id

    def send_message(self, cache_s=0, **kwargs):

        data = SYSTEM_ALERT_MESSAGES[self.message_type]["data"]

        mod_data = {}
        for lang in data.keys():
            txt = data[lang]
            for kw in kwargs.keys():
                txt = re.sub(f"%{kw}", f"{kwargs[kw]}", txt)
            mod_data[lang] = txt

        alert = ClusterRoleAlert(
            cluster_id=self.cluster_id,
            application_role_id=self.application_role_id,
            alert_type_id=self.alert_type_id,
            data=mod_data,
            created_by_id=self.user_id

        )
        if cache_s:
            # we don't want to spam our users:
            scrambled_alert = hashlib.md5(f'{alert.cluster_id}-{alert.application_role_id}-{alert.alert_type_id}-{alert.data}'.encode('UTF-8')).hexdigest()
            if cache.get(f"SystemAlertMessage-{scrambled_alert}"):
                return True
            cache.set(f"SystemAlertMessage-{scrambled_alert}", True, cache_s)

        alert.save()
        if alert.id:
            return True
        else:
            return False
