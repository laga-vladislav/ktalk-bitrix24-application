from environs import Env

env = Env()
env.read_env(override=True)

CLIENT_ID = env.str("CLIENT_ID")
CLIENT_SECRET = env.str("CLIENT_SECRET")
CLIENT_WEBHOOK = env.str("CLIENT_WEBHOOK")
