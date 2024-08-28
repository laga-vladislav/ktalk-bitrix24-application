from fastapi import Request
from datetime import datetime
from crest.crest import CRestBitrix24


def get_crest(request: Request) -> CRestBitrix24:
    return request.app.state.CRest
