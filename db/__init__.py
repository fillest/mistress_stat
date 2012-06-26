import sapyens.db

from sapyens.db import Reflected

DBSession, QueryPropertyMixin = sapyens.db.make_classes(use_zope_ext = False)

def init (engine):
	sapyens.db.init(engine, DBSession, Reflected)
