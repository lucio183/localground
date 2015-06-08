from localground.apps.site.api.tests.base_tests import ModelMixin
from django import test
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models.query import QuerySet
from django.db.models import Q

from localground.apps.lib.helpers.sqlparse.sqlparser import QueryParser
from localground.apps.lib.helpers.sqlparse.sql_djangoify import get_where_clause, split_statements, get_where_conditions
from localground.apps.site import models

# model imports
from localground.apps.site.models.marker import Marker
from localground.apps.site.models.photo import Photo

def get_data_sets_from_sql(model, raw_where_clause, parsed_where_clause=None):
    """
    Get's a data set for the given model,using provided where_clause, using
    raw sql and the QueryParser. Datasets are ordered by id and limited to 10
    entries.

    returns a dataset based on raw execution and a dataset based on parsed execution

    params:
    model - django model being queried
    raw_where_clause - string of sql query to be used for raw data set
    parsed_where_clause - string of sql query to be used for parsed data set
    """
    if not parsed_where_clause:
        parsed_where_clause = raw_where_clause

    raw_sql = "SELECT * FROM {} {} ORDER BY ID LIMIT 10"\
            .format(model._meta.db_table, raw_where_clause)

    parsed_sql = "SELECT * FROM {} {}"\
            .format(model._meta.db_table, parsed_where_clause)
    raw_dataset = model.objects.raw(raw_sql.replace("%", "%%")) # % signs need to be escaped or the connection expects parameters

    f = QueryParser(model, parsed_sql)
    parsed_dataset = f.extend_query(model.objects.order_by('id'))[:10]

    return raw_dataset, parsed_dataset


class SQLStatementTest(test.TestCase):
    """
    Tests for code that pulls statements out of sql.
    """
    def test_where_clause_should_extract(self):
        where = "col1 = val 1"
        sql = "select * from stuff where " + where
        self.assertEqual(where, get_where_clause(sql))

        sql = "select * from stuff where " + where + " order by stuff"
        self.assertEqual(where, get_where_clause(sql))

        sql = "select * from stuff where " + where + " order by stuff limit 10"
        self.assertEqual(where, get_where_clause(sql))

    def test_statement_extraction(self):
        statements = [
                "col1 = val1",
                "and",
                "col2 = val2",
                "and",
                "col3 = 'a and b'"
                ]
        test = split_statements(" ".join(statements))
        for a, b in zip (statements, test):
            self.assertEqual(a, b)

    def test_where_conditions(self):
        statements = [
                "col1 = val1",
                "and",
                "col2 = val2",
                "and",
                "col3 = 'a and b'"
                ]
        sql = "select * from stuff where {}".format(" ".join(statements))
        test = get_where_conditions(sql)

        for a, b in zip (statements, test):
            self.assertEqual(a, b)


class SQLParseTest(test.TestCase, ModelMixin):
    fixtures = ['initial_data.json', 'test_data.json']
    
    def setUp(self):
        '''
        Create some dummy data using the ModelMixin, to make sure that the queries
        are actually matching, given the data.
        '''
        ModelMixin.setUp(self)
        self.photo1 = self.create_photo(self.user, self.project, file_name='2013-07-04 16.56.55.jpg', point=Point(-122.246, 37.896))
        self.photo2 = self.create_photo(self.user, self.project, file_name='2013-06-30 18.25.38.jpg', point=Point(-122.846, 37.396),
                                        device='SCH-I535')

    def compare_sql(self, model, raw_where, parsed_where=None):
        raw_dataset, parsed_dataset = get_data_sets_from_sql(model, raw_where, parsed_where)
        n = 0
        for r, p in zip(raw_dataset, parsed_dataset):
            n+=1
            self.assertEqual(r.id, p.id)

        if n== 0:
            raw_count = len(list(raw_dataset))
            parsed_count = len(list(parsed_dataset))
            self.fail("no results to compare - raw:{} parsed:{}".format(raw_count, parsed_count))

    def test_no_where_should_be_equal(self, **kwargs):
        self.compare_sql(Photo, "")

    def test_equality_operator(self, **kwargs):
        # test string compare
        self.compare_sql(Photo, "WHERE file_name_orig='%s'" % (self.photo1.file_name_orig))

        # test number compare
        self.compare_sql(Photo, "WHERE id<%s" % self.photo2.id,)

    def test_and_conjunction(self):
        self.compare_sql(Photo, "WHERE device='SCH-I535' and id < %s" % self.photo1.id,)

    def test_or_conjunction(self):
        self.compare_sql(Photo, "WHERE device='SCH-I535' or id < %s" % self.photo1.id,)

    def test_like_operator(self):
        self.compare_sql(Photo, "WHERE device like '%I5%'")

    def test_startswith_operator(self):
        self.compare_sql(Photo, "WHERE device like 'HTC%'")


    def test_endswith_operator(self):
        self.compare_sql(Photo, "WHERE device like '%535'")


    def test_in_operator(self):
        self.compare_sql(Photo, "WHERE file_name_orig in ('{}', '{}')".format(self.photo1.file_name_orig, self.photo2.file_name_orig))
        self.compare_sql(Photo, "WHERE id in ({},{})".format(self.photo1.id, self.photo2.id))
        
    '''
    def test_geo_query(self, **kwargs):
        raw_where = "WHERE ST_DISTANCE(point, ST_SetSRID(ST_MakePoint(-122.246, 37.896), 4326)) < 1"
        parsed_where = "WHERE point in buffer(-122.246, 37.896, 1)"
        self.compare_sql(Photo, raw_where, parsed_where)
    '''
        
    def test_geo_query_new(self, **kwargs):
        sql = "WHERE point within buffer(-122.246, 37.896, 1000)" #return all photos within 1,000 meters
        f = QueryParser(Photo, sql)
        parsed_dataset = f.extend_query(Photo.objects.order_by('id'))
        #expect two photos to return 
        self.assertEqual(len(parsed_dataset), 2)
        
        sql = "WHERE point within buffer(-122.246, 37.896, 10)" #return all photos within 10 meters
        f = QueryParser(Photo, sql)
        parsed_dataset = f.extend_query(Photo.objects.order_by('id'))
        #expect 1 photo to return 
        self.assertEqual(len(parsed_dataset), 1)
        

    def test_simple_geo_query(self):
        point = Point(-122.246, 37.896)
        Photo.objects.filter(point__distance_lt=(point, D(m=5)))
