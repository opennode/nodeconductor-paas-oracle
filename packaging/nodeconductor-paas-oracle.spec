Name: nodeconductor-paas-oracle
Summary: Oracle PaaS plugin for NodeConductor
Group: Development/Libraries
Version: 0.3.0
Release: 1.el7
License: Copyright 2016 OpenNode LLC.  All rights reserved.
Url: http://nodeconductor.com
Source0: %{name}-%{version}.tar.gz

Requires: nodeconductor >= 0.101.2
Requires: nodeconductor-jira >= 0.1.0
Requires: nodeconductor-openstack >= 0.5.0

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires: python-setuptools

%description
Oracle PaaS plugin for NodeConductor.

%prep
%setup -q -n %{name}-%{version}

%build
python setup.py build

%install
rm -rf %{buildroot}
python setup.py install --single-version-externally-managed -O1 --root=%{buildroot} --record=INSTALLED_FILES

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Wed Aug 17 2016 Jenkins <jenkins@opennodecloud.com> - 0.3.0-1.el7
- New upstream release

* Mon Aug 8 2016 Jenkins <jenkins@opennodecloud.com> - 0.2.3-1.el7
- New upstream release

* Thu Aug 4 2016 Jenkins <jenkins@opennodecloud.com> - 0.2.2-1.el7
- New upstream release

* Thu Aug 4 2016 Jenkins <jenkins@opennodecloud.com> - 0.2.1-1.el7
- New upstream release

* Thu Aug 4 2016 Jenkins <jenkins@opennodecloud.com> - 0.2.0-1.el7
- New upstream release

* Thu Apr 21 2016 Juri Hudolejev <juri@opennodecloud.com> - 0.1.0-1.el7
- Initial version of the package

