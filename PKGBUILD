# Maintainer: Miguel
pkgname=aetheris-file-manager-by-miguel-git
_gitname=aetheris-file-manager-by-miguel
pkgver=0.1.0.r0
pkgrel=1
pkgdesc="Aetheris File Manager by Miguel - Universal PyQt6 file manager"
arch=('any')
url="https://github.com/SEU_USUARIO/aetheris-file-manager-by-miguel"
license=('GPL-3.0-or-later')
depends=('python' 'python-pyqt6' 'xdg-utils')
makedepends=('git' 'python-build' 'python-installer' 'python-wheel' 'python-setuptools')
provides=('aetheris-file-manager-by-miguel')
conflicts=('aetheris-file-manager-by-miguel')
source=("git+${url}.git"
        "aetheris-file-manager-by-miguel.desktop")
sha256sums=('SKIP'
            'SKIP')

pkgver() {
    cd "${srcdir}/${_gitname}"
    printf "0.1.0.r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

build() {
    cd "${srcdir}/${_gitname}"
    python -m build --wheel --no-isolation
}

package() {
    cd "${srcdir}/${_gitname}"
    python -m installer --destdir="${pkgdir}" dist/*.whl
    install -Dm644 "${srcdir}/aetheris-file-manager-by-miguel.desktop" "${pkgdir}/usr/share/applications/aetheris-file-manager-by-miguel.desktop"
}
