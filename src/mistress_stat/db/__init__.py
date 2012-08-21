import sapyens.db

from sapyens.db import Reflected

DBSession, QueryPropertyMixin, ScopedSessionMixin = sapyens.db.make_classes(use_zope_ext = False)


class Model (Reflected, QueryPropertyMixin, ScopedSessionMixin):
	__abstract__ = True


def init (engine):
	sapyens.db.init(engine, DBSession, Reflected, on_before_reflect = _on_before_reflect)

def _on_before_reflect ():
	import mistress_stat.db.models
	Reflected.metadata.reflect()  #TODO for n-n tables
