from __future__ import unicode_literals

import pprint
import socket

from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from nodeconductor.openstack.models import Tenant
from nodeconductor_paas_oracle.models import OracleService, OracleServiceProjectLink, Flavor, Deployment
from nodeconductor.template.models import TemplateGroup, Template


class Command(BaseCommand):
    help_text = "Create template for Oracle Deployment provisioning"

    def handle(self, *args, **options):
        host = 'http://%s' % (socket.gethostname() or '127.0.0.1:8000')
        self.base_url = host
        self.stdout.write(self.style.MIGRATE_HEADING('Preparation:'))
        self.base_url = (raw_input('Please enter NodeConductor base URL [%s]: ' % host) or host)
        self.base_url = self.base_url.rstrip('/')
        self.templates = []

        self.stdout.write(self.style.MIGRATE_HEADING('\nConfigure Oracle Deployment'))

        self.stdout.write('\nChoose Oracle Service:')

        services = list(OracleService.objects.order_by('name'))
        start = 1
        for i in range(0, len(services), 3):
            choices = []
            for idx, val in enumerate(services[i:i + 3], start):
                choices.append('\t[{:3}] {:<30}'.format(idx, val))
            self.stdout.write(''.join(choices))
            start += 3

        while True:
            idx = (raw_input(self.style.WARNING('Desired Service [1]: ')) or '1')
            try:
                service = services[int(idx) - 1]
            except (IndexError, TypeError, ValueError):
                self.stdout.write(self.style.NOTICE('\tWrong Service'))
            else:
                break

        options = {'service': self.get_obj_url('oracle-detail', service)}

        self.stdout.write('\nChoose Project:')

        spls = list(OracleServiceProjectLink.objects.filter(service=service).order_by('project__name'))
        start = 1
        for i in range(0, len(spls), 3):
            choices = []
            for idx, val in enumerate(spls[i:i + 3], start):
                choices.append('\t[{:3}] {:<30}'.format(idx, val.project.name))
            self.stdout.write(''.join(choices))
            start += 3

        while True:
            idx = (raw_input(self.style.WARNING('Desired Project [1]: ')) or '1')
            try:
                spl = spls[int(idx) - 1]
            except (IndexError, TypeError, ValueError):
                self.stdout.write(self.style.NOTICE('\tWrong Project'))
            else:
                options['project'] = self.get_obj_url('project-detail', spl.project)
                break

        self.stdout.write('\nChoose Flavor:')

        flavors = list(Flavor.objects.order_by('name'))
        start = 1
        for i in range(0, len(flavors), 3):
            choices = []
            for idx, val in enumerate(flavors[i:i + 3], start):
                info = '{0.name} (cores={0.cores}, ram={0.ram}, disk={0.disk})'.format(val)
                choices.append('\t[{:3}] {:<30}'.format(idx, info))
            self.stdout.write(''.join(choices))
            start += 3

        while True:
            idx = (raw_input(self.style.WARNING('Desired Flavor [1]: ')) or '1')
            try:
                flavor = flavors[int(idx) - 1]
            except (IndexError, TypeError, ValueError):
                self.stdout.write(self.style.NOTICE('\tWrong Flavor'))
            else:
                options['flavor'] = self.get_obj_url('oracle-flavors-detail', flavor)
                break

        self.stdout.write('\nChoose Tenant:')

        tenants = list(Tenant.objects.filter(service_project_link__project=spl.project).order_by('name'))
        start = 1
        for i in range(0, len(tenants), 3):
            choices = []
            for idx, val in enumerate(tenants[i:i + 3], start):
                choices.append('\t[{:3}] {:<30}'.format(idx, val.name))
            self.stdout.write(''.join(choices))
            start += 3

        while True:
            idx = (raw_input(self.style.WARNING('Desired Tenant [1]: ')) or '1')
            try:
                tenant = tenants[int(idx) - 1]
            except (IndexError, TypeError, ValueError):
                self.stdout.write(self.style.NOTICE('\tWrong Tenant'))
            else:
                options['tenant'] = self.get_obj_url('openstack-tenant-detail', tenant)
                break

        options['db_size'] = self.input_int('Data storage size, GB [10]: ', 10)
        options['db_arch_size'] = self.input_int('Archive storage size, GB [10]: ', 10)
        options['db_type'] = self.input_choice('database type', Deployment.Type.CHOICES)
        options['db_version'] = self.input_choice('database version', Deployment.Version.CHOICES)
        options['db_template'] = self.input_choice('database template', Deployment.Template.CHOICES)
        options['db_charset'] = self.input_choice('database charset', Deployment.Charset.CHOICES)
        options['user_data'] = (raw_input(self.style.WARNING('Additional data, text: ')) or '')

        self.templates.append(Template(
            object_content_type=ContentType.objects.get_for_model(Deployment),
            options=options,
        ))

        default_name = 'Oracle PaaS (%s)' % service.name.replace(' ', '')
        name = raw_input(self.style.WARNING('Enter template group name [%s]:' % default_name)) or default_name
        group = TemplateGroup(name=name)

        # ********* REVIEW *********
        self.stdout.write(self.style.MIGRATE_HEADING('\nReview and create'))
        templates = []
        for template in self.templates:
            templates.append({
                'type': str(template.object_content_type),
                'options': template.options,
            })

        final = [
            ('name', group.name),
            ('templates', templates),
        ]

        pp = pprint.PrettyPrinter(depth=6)
        self.stdout.write(pp.pformat(final))

        while True:
            opt = (raw_input(self.style.WARNING('Create? [Y/n]: ')) or 'y').lower()
            if opt == 'n':
                self.stdout.write(self.style.NOTICE('Terminate!'))
                return
            elif opt == 'y':
                break

        # ******** CREATING TEMPLATES ********
        created_instances = []
        try:
            group.save()
            group.tags.add('PaaS')
            created_instances.append(group)

            for idx, template in enumerate(self.templates, start=1):
                template.order_number = idx
                template.group = group
                template.save()
                template.tags.add('PaaS')
        except:
            self.stdout.write(self.style.NOTICE('\tError happened -- rollback!'))
            for instance in created_instances:
                instance.delete()
            raise

        self.stdout.write(self.style.MIGRATE_SUCCESS('Done.'))

    def get_obj_url(self, name, obj):
        return self.base_url + reverse(name, args=(obj.uuid.hex if hasattr(obj, 'uuid') else obj.pk,))

    def input_int(self, message, default_value):
        while True:
            try:
                return int(raw_input(self.style.WARNING(message)) or default_value)
            except ValueError:
                self.stdout.write('\nInputed value should be integer, please try again.')

    def input_choice(self, message, choices):
        self.stdout.write('\nChoose %s:' % message)
        for idx, data in enumerate(choices, start=1):
            self.stdout.write('\t[{:3}] {:<30}'.format(idx, data[1]))

        while True:
            idx = (raw_input(self.style.WARNING('Desired %s [1]: ' % message)) or '1')
            try:
                val = choices[int(idx) - 1]
            except (IndexError, TypeError, ValueError):
                self.stdout.write(self.style.NOTICE('\tWrong %s' % message))
            else:
                return val[0]
