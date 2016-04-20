from nodeconductor.structure import perms as structure_perms


PERMISSION_LOGICS = (
    ('oracle_paas.OracleService', structure_perms.service_permission_logic),
    ('oracle_paas.OracleServiceProjectLink', structure_perms.service_project_link_permission_logic),
    ('oracle_paas.Deployment', structure_perms.resource_permission_logic),
)
