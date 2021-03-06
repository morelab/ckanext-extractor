# -*- coding: utf8 -*- 

from sqlalchemy import desc
from ckanext.extractor.model.transformation_model import Extraction
import datetime
from logging import getLogger

WORKING = u'working'
ERROR = u'error'
OK = u'ok'

log = getLogger(__name__)

class ExtractionContext():

	def __init__(self, transformation, session):
		self.transformation = transformation
		self.session = session

		#initialize current status using database information if it exists
		self.extraction = session.query(Extraction).filter_by(transformation_id=transformation.package_id).order_by(desc(Extraction.start_date)).first()

		if self.extraction is None:
			self.extraction = Extraction(datetime.datetime.now(), '{}', WORKING)
			self.transformation.extractions.append(self.extraction)
		else:
			self.extraction = Extraction(datetime.datetime.now(), self.extraction.context, WORKING)
			self.transformation.extractions.append(self.extraction)

		self.session.merge(self.transformation)
		self.session.commit()

	def update_context(self, new_context):
		log.info('Updating context for extraction %s of transformation %s' % (self.extraction.id, self.transformation.package_id))
		self.extraction.context = unicode(new_context)
		self.session.merge(self.transformation)
		self.session.commit()

	def get_current_context(self):
		return eval(self.extraction.context)

	def finish_ok(self, comment):
		log.info('Extraction %s of transformation %s finished with status OK. Comment: %s' % (self.extraction.id, self.transformation.package_id, comment))
		self.extraction.end_date = datetime.datetime.now()
		self.extraction.transformation_status = OK
		self.extraction.comment = comment
		self.session.merge(self.transformation)
		self.session.commit()

	def finish_error(self, comment):
		log.info('Extraction %s of transformation %s finished with status ERROR. Comment: %s' % (self.extraction.id, self.transformation.package_id, comment))
		self.extraction.end_date = datetime.datetime.now()
		self.extraction.transformation_status = ERROR
		self.extraction.comment = comment
		self.session.merge(self.transformation)
		self.session.commit()