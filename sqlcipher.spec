#
# Conditional build:
%bcond_with	tests		# run tests [broken]
%bcond_with	tcl		# Tcl extension [not adapted to sqlcipher name]
%bcond_without	unlock_notify	# disable unlock notify API
%bcond_without	load_extension	# enable load extension API
%bcond_with	icu		# ICU tokenizer support

%define		tclver		8.6
Summary:	SQLCipher library - SQLite extension that provides AES encryption
Summary(pl.UTF-8):	Biblioteka SQLCipher - rozszerzenie SQLite zapewniające szyfrowanie AES
Name:		sqlcipher
Version:	3.4.2
Release:	2
License:	BSD
Group:		Libraries
# Source0Download: https://github.com/sqlcipher/sqlcipher/releases
Source0:	https://github.com/sqlcipher/sqlcipher/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	b224b7a3a1927d2e6344ae6e27308c8c
URL:		https://www.zetetic.net/sqlcipher/
%{?with_load_extension:Provides:	%{name}(load_extension)}
%{?with_unlock_notify:Provides:	%{name}(unlock_notify)}
%{?with_icu:Provides:	%{name}(icu)}
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	openssl-devel
BuildRequires:	readline-devel
%{?with_load_extension:BuildRequires:	sed >= 4.0}
BuildRequires:	tcl
%{?with_tcl:BuildRequires:	tcl-devel >= %{tclver}}
BuildRequires:	unzip
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_ulibdir	/usr/lib

%description
SQLCipher is an SQLite extension that provides transparent 256-bit AES
encryption of database files. Pages are encrypted before being written
to disk and are decrypted when read back. Due to the small footprint
and great performance it's ideal for protecting embedded application
databases and is well suited for mobile development.

%description -l pl.UTF-8
SQLCipher to rozszerzenie SQLite zapewniające przezroczyste,
256-bitowe szyfrowanie AES plików baz danych. Strony są szyfrowane
przed zapisem na dysk, a odszyfrowywane przy odczycie. Dzięki
niewielkiemu narzutowi i dużej wydajności jest to idealne rozwiązanie
do zabezpieczania baz danych aplikacji wbudowanych, dobrze nadaje się
do tworzenia oprogramowania dla urządzeń przenośnych.

%package devel
Summary:	Header files for SQLCipher library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki SQLCipher
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	openssl-devel
%if %{with unlock_notify}
Provides:	%{name}-devel(unlock_notify)
%endif
%if %{with load_extension}
Provides:	%{name}-devel(load_extension)
%endif
%if %{with icu}
Provides:	%{name}-devel(icu)
%endif

%description devel
Header files for SQLCipher library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki SQLCipher.

%package static
Summary:	Static SQLCipher library
Summary(pl.UTF-8):	Statyczna biblioteka SQLCipher
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}
%if %{with unclock_notify}
Provides:	%{name}-static(unlock_notify)
%endif
%if %{with load_extension}
Provides:	%{name}-static(load_extension)
%endif

%description static
Static SQLCipher library.

%description static -l pl.UTF-8
Statyczna biblioteka SQLCipher.

%package -n tcl-%{name}
Summary:	sqlite3 tcl extension
Summary(pl.UTF-8):	Rozszerzenie sqlite3 dla Tcl
Group:		Development/Languages/Tcl

%description -n tcl-%{name}
sqlite3 tcl extension.

%description -n tcl-%{name} -l pl.UTF-8
Rozszerzenie sqlite3 dla Tcl.

%prep
%setup -q

%build
cp -f /usr/share/automake/config.sub .
%{__libtoolize}
%{__aclocal}
%{__autoconf}

append-cppflags() {
	CPPFLAGS="$CPPFLAGS $*"
}
append-libs() {
	LIBS="$LIBS $*"
}
export CPPFLAGS="%{rpmcflags}"
export LIBS
%if %{with tcl}
export TCLLIBDIR="%{tcl_sitearch}/sqlite3"
%endif

append-cppflags -DSQLITE_DISABLE_DIRSYNC=1 -DSQLITE_SECURE_DELETE

# requirement of sqlcipher
append-cppflags -DSQLITE_HAS_CODEC

# Support column metadata functions.
# http://sqlite.org/c3ref/column_database_name.html
# http://sqlite.org/c3ref/table_column_metadata.html
append-cppflags -DSQLITE_ENABLE_COLUMN_METADATA

# Support Full-Text Search versions 3 and 4.
# http://sqlite.org/fts3.html
#append-cppflags -DSQLITE_ENABLE_FTS3 -DSQLITE_ENABLE_FTS3_PARENTHESIS -DSQLITE_ENABLE_FTS4 -DSQLITE_ENABLE_FTS4_UNICODE61
append-cppflags -DSQLITE_ENABLE_FTS3 -DSQLITE_ENABLE_FTS3_PARENTHESIS

# Support R*Trees.
# http://sqlite.org/rtree.html
append-cppflags -DSQLITE_ENABLE_RTREE

# Support soundex() function.
# http://sqlite.org/lang_corefunc.html#soundex
#append-cppflags -DSQLITE_SOUNDEX

# Support dbstat virtual table.
# https://www.sqlite.org/dbstat.html
append-cppflags -DSQLITE_ENABLE_DBSTAT_VTAB

%if %{with unlock_notify}
# Support unlock notification.
# http://sqlite.org/unlock_notify.html
append-cppflags -DSQLITE_ENABLE_UNLOCK_NOTIFY
%endif

%if %{with icu}
append-cppflags -DSQLITE_ENABLE_ICU
append-libs "-licui18n -licuuc"
%endif

%if %{with load_extension}
append-libs "-ldl"
%endif

%configure \
	%{!?with_tcl:--disable-tcl}%{?with_tcl:--with-tcl=%{_ulibdir}} \
	%{__enable_disable load_extension load-extension} \
	--enable-tempstore \
	--enable-threadsafe

%{__make}

%{?with_tests:LC_ALL=C %{__make} test}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_mandir}/man1

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

cp -p sqlcipher.1 $RPM_BUILD_ROOT%{_mandir}/man1

# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libsqlcipher.la

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc CHANGELOG.md LICENSE README.md
%attr(755,root,root) %{_bindir}/sqlcipher
%attr(755,root,root) %{_libdir}/libsqlcipher.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libsqlcipher.so.0
%{_mandir}/man1/sqlcipher.1*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libsqlcipher.so
%{_includedir}/sqlcipher
%{_pkgconfigdir}/sqlcipher.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libsqlcipher.a

%if %{with tcl}
%files -n tcl-%{name}
%defattr(644,root,root,755)
%dir %{_libdir}/tcl*/sqlite3
%attr(755,root,root) %{_libdir}/tcl%{tclver}/sqlite3/libtclsqlite3.so
%{_libdir}/tcl%{tclver}/sqlite3/pkgIndex.tcl
%endif
