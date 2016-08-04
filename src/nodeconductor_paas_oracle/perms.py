from nodeconductor.core.permissions import StaffPermissionLogic
from nodeconductor.structure import perms as structure_perms


PERMISSION_LOGICS = (
    ('nodeconductor_paas_oracle.OracleService', structure_perms.service_permission_logic),
    ('nodeconductor_paas_oracle.OracleServiceProjectLink', structure_perms.service_project_link_permission_logic),
    ('nodeconductor_paas_oracle.Deployment', structure_perms.resource_permission_logic),
    ('nodeconductor_paas_oracle.Flavor', StaffPermissionLogic(any_permission=True)),
)
