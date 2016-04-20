from django.db import models

from nodeconductor.structure import models as structure_models


class OracleService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='oracle_services', through='OracleServiceProjectLink')

    @classmethod
    def get_url_name(cls):
        return 'oracle'


class OracleServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(OracleService)

    @classmethod
    def get_url_name(cls):
        return 'oracle-spl'


class Deployment(structure_models.Resource):

    service_project_link = models.ForeignKey(
        OracleServiceProjectLink, related_name='deployments', on_delete=models.PROTECT)

    report = models.TextField(blank=True)

    @classmethod
    def get_url_name(cls):
        return 'oracle-deployments'
