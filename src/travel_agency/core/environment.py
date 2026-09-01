from os import environ


def get_or_raise(key, dictionary=environ, exception_to_raise=KeyError):
    if key not in dictionary:
        raise exception_to_raise("{} not found in envs".format(key))
    return dictionary[key]


class Environment:
    BASE_URL: str = get_or_raise("BASE_URL")
    API_KEY: str = get_or_raise("API_KEY")
    MODEL: str = get_or_raise("MODEL")

    MEM0_API_KEY: str = get_or_raise("MEM0_API_KEY")