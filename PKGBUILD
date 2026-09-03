pkgname=aetheris-file-manager-by-miguel
pkgver=0.1.0
pkgrel=1
pkgdesc="Standalone lightweight modern file manager built with PyQt6"
arch=('any')
url="https://github.com/migsaito/aetheris-file-manager-by-miguel"
license=('MIT')
depends=('python' 'python-pyqt6' 'qt6-svg' 'xdg-utils')
makedepends=('python-build' 'python-installer' 'python-setuptools' 'python-wheel')
source=("$pkgname::git+https://github.com/migsaito/aetheris-file-manager-by-miguel.git")
sha256sums=('SKIP')

build() {
    cd "$srcdir/$pkgname"
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/$pkgname"
    python -m installer --destdir="$pkgdir" dist/*.whl
    install -Dm644 aetheris-file-manager-by-miguel.desktop "$pkgdir/usr/share/applications/aetheris-file-manager-by-miguel.desktop"
    install -Dm644 logo.png "$pkgdir/usr/share/icons/hicolor/512x512/apps/aetheris-file-manager-by-miguel.png"
    install -Dm644 logo.png "$pkgdir/usr/share/icons/hicolor/256x256/apps/aetheris-file-manager-by-miguel.png"
    install -Dm644 logo.png "$pkgdir/usr/share/icons/hicolor/scalable/apps/aetheris-file-manager-by-miguel.png"
    install -Dm644 logo.png "$pkgdir/usr/share/pixmaps/aetheris-file-manager-by-miguel.png"
}
