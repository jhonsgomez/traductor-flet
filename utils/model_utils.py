import pickle


def load_model(path: str):
    with open(path, "rb") as f:
        md = pickle.load(f)
    return md["modelo"]
