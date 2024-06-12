import threading


end_time = None

sites_to_block = []
common_filters = [
    "www.instagram.com",
    "www.facebook.com",
    "www.vk.com",
    "www.youtube.com",
    "www.telegram.com",
    "www.one-piece.ru",
    "www.twitch.tv",
]

hosts_path = "/etc/hosts"
redirect = "127.0.0.1"


def session_maker(func):
    def inner(seconds=None):
        if seconds:
            func()
            timer = threading.Timer(seconds, unblock_sites)
            timer.start()
        else:
            func()

    return inner


@session_maker
def block_sites():
    with open(hosts_path, "r+") as hostsfile:
        hosts_content = hostsfile.read()
        for site in sites_to_block:
            if site not in hosts_content:
                hostsfile.write(redirect + " " + site + "\n")


def unblock_sites():
    with open(hosts_path, "r+") as hostsfile:
        lines = hostsfile.readlines()
        hostsfile.seek(0)
        for line in lines:
            if not any(site in line for site in sites_to_block):
                hostsfile.write(line)
        hostsfile.truncate()


unblock_sites()
