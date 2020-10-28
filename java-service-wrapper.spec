%global javaver 1.7
%global hgrev   3290d306074a
%global pname yaja-wrapper
%if ! 0%{?__isa_bits}
%ifarch x86_64 ia64 ppc64 sparc64 s390x alpha ppc64le aarch64
%global __isa_bits 64
%else
%global __isa_bits 32
%endif
%endif
%global __provides_exclude_from ^%{_libdir}/%{name}/.*\.so$
%bcond_with     docs
%global cocoon  cocoon-2.0.4
Name:                java-service-wrapper
Version:             3.2.5
Release:             1
Summary:             Java service wrapper
License:             MIT
URL:                 https://bitbucket.org/ivertex/yaja-wrapper
Source0:             https://bitbucket.org/ivertex/yaja-wrapper/get/release-3_2_5.tar.bz2
Source1:             %{name}.template.init
Source2:             %{name}-%{version}-docs.tar.bz2
%if %{with docs}
Source3:             http://archive.apache.org/dist/cocoon/BINARIES/%{cocoon}-bin.tar.gz
%endif
Source4:             http://repo1.maven.org/maven2/tanukisoft/wrapper/3.2.3/wrapper-3.2.3.pom
Patch0:              %{name}-3.2.4-cflags.patch
Patch1:              %{name}-3.2.4-jnilibpath.patch
Patch2:              %{name}-3.2.4-docbuild.patch
Patch3:              %{name}-3.2.5-rhbz1037144.patch
Patch98:             Use-RPM_OPT_FLAGS-on-s390x.patch
Patch99:             ppc64le-support.patch
BuildRequires:       ant javapackages-local gcc make
%description
The Java Service Wrapper enables a Java application to be run as a
Unix daemon.  It also monitors the health of your application and JVM.

%package        javadoc
Summary:             API documentation for %{name}
BuildArch:           noarch
%description    javadoc
API documentation for %{name}.

%prep
%setup -q -n ivertex-%{pname}-%{hgrev}  -a 2
sed '/<version>/s/>.*</>%{version}</' %{SOURCE4} >pom.xml
install -pm 644 %{SOURCE1} doc/template.init
%patch0 -p1
sed -e 's|@LIBPATH@|%{_libdir}/%{name}|' %{PATCH1} | %{__patch} -p1 -F 0
%patch2 -p0
%patch3
%patch98 -p1
%patch99 -p1
%if %{with docs}
mkdir tools ; cd tools
tar xf %{SOURCE3}
unzip -q %{cocoon}/cocoon.war ; mv WEB-INF/lib %{cocoon}/
cd ..
%endif
(cd src/c; cp Makefile-linux-ppc64le-64.make Makefile-linux-aarch64-64.make)
(cd src/c; cp Makefile-linux-arm-32.make Makefile-linux-aarch32-32.make)

%build
%ant -Dbits=%{__isa_bits} -Djavac.target.version=%{javaver}
%javadoc -sourcepath src/java -Xdoclint:none -d javadoc -link %{_javadocdir}/java -author \
    -windowtitle "Java Service Wrapper API" -doctitle "Java Service Wrapper" \
    -version $(find src/java -name "*.java" -not -path "*/test/*")
%if %{with docs}
rm -r doc/english
%ant -Dbits=%{__isa_bits} doc
%endif

%install
install -Dpm 755 bin/wrapper $RPM_BUILD_ROOT%{_sbindir}/java-service-wrapper
install -dm 755 $RPM_BUILD_ROOT%{_libdir}/%{name}
install -pm 755 lib/libwrapper.so $RPM_BUILD_ROOT%{_libdir}/%{name}
%mvn_file : %{name} %{_libdir}/%{name}/wrapper
%mvn_artifact pom.xml lib/wrapper.jar
%mvn_install -J javadoc

%files -f .mfiles
%doc AboutThisRepository.txt doc/
%{_sbindir}/java-service-wrapper
%{_libdir}/%{name}/
%license doc/license.txt

%files javadoc -f .mfiles-javadoc
%license doc/license.txt

%changelog
* Wed Oct 28 2020 shaoqiang kang <kangshaoqiang1@huawei.com> - 3.2.5-1
- Package init
