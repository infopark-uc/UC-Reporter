# Default params
class cucm_servers_list():

    cucm_dict = {
        "MSK": {"IPAddress": "10.250.10.10", "login": "webadmin", "password": "CCMAdminSSK"},
        "KF": {"IPAddress": "10.250.34.10", "login": "webadmin", "password": "CCMAdminSSK"},
        "NF": {"IPAddress": "10.250.62.10", "login": "webadmin", "password": "CCMAdminSSK"},
        "TF": {"IPAddress": "10.250.44.10", "login": "webadmin", "password": "CCMAdminSSK"},
        "NU": {"IPAddress": "10.250.74.10", "login": "webadmin", "password": "CCMAdminSSK"},
        "Infocell": {"IPAddress": "172.20.5.10", "login": "webadmin", "password": "CCMAdminUC"}
    }

class in_room_control_access_data():
    codec_access_data = {
        "ip_address": "172.20.5.5",
        "login": "admin",
        "password": "CCMAdminUC"
    }

    ipphone_access_data = {
        "ip_address": "172.20.5.144",
        "login": "screenshotuser",
        "password": "Qwerty123"
    }

    wifi_access_data = {
        "ip_address": "172.20.31.254",
        "login": "cisco",
        "password": "cisco"
    }

    ap_list = [" "]