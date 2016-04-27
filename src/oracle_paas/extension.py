from nodeconductor.core import NodeConductorExtension


class OracleExtension(NodeConductorExtension):

    class Settings:
        ORACLE_TICKET_TEMPLATES = {
            'provision': {
                'summary': "Request for a new Oracle DB PaaS instance",
                'details': """
                    Oracle DB purchase details

                    Customer name: {customer.name}
                    Project name: {project.project_group.name}
                    Environment name: {project.name}
                    Customer UUID: {customer.uuid.hex}
                    Project UUID: {project.project_group.uuid.hex}
                    Environment UUID: {project.uuid.hex}
                    OpenStack tenant id: {deployment.tenant.uuid.hex}

                    Hardware Configuration:
                    Name: {deployment.name}
                    Flavor: {deployment.flavor_info}
                    SSH key: {ssh_key.name}
                    SSH key UUID: {ssh_key.uuid.hex}

                    Oracle DB Configuration:
                    Name: {deployment.db_name}
                    Size: {deployment.db_size} GB
                    Version: {deployment.db_version} {deployment.db_type}
                    Database type: {deployment.db_template}
                    Character set: {deployment.db_charset}
                    Additional data: {deployment.user_data}
                """,
            },
            'undeploy': {
                'summary': "Request for removing Oracle DB PaaS instance",
                'details': """
                    Oracle DB details

                    Name: {deployment.name}
                    UUID: {deployment.uuid.hex}
                    Customer name: {customer.name}
                    Project name: {project.project_group.name}
                    Environment name: {project.name}
                    Customer UUID: {customer.uuid.hex}
                    Project UUID: {project.project_group.uuid.hex}
                    Environment UUID: {project.uuid.hex}
                """,
            },
            'resize': {
                'summary': "Request for resizing Oracle DB PaaS instance",
                'details': """
                    Oracle DB details

                    Name: {deployment.name}
                    UUID: {deployment.uuid.hex}
                    Customer name: {customer.name}
                    Project name: {project.project_group.name}
                    Environment name: {project.name}
                    Customer UUID: {customer.uuid.hex}
                    Project UUID: {project.project_group.uuid.hex}
                    Environment UUID: {project.uuid.hex}

                    Hardware Configuration:
                    Flavor: {deployment.flavor_info}
                """,
            },
        }

    @staticmethod
    def django_app():
        return 'oracle_paas'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in
