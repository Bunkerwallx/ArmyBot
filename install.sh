paquetes = [python pacman apt dpkg zypper emerge bash shell]
ip=''

checkInter() {
     if ping -c 3 https://go.com; then
         echo "Coneccion de internet correcta 200 ok...... ya chingaste paleta cristo"
    elif checkInter()
         echo ""
}

buscarPack() {
    if which $paquetes; then
       echo "Instalando dependencias y paquetes......"
    elif pacman -Sy $paquetes --needed --overwrite='*' --noconfirm
       echo "error al installar................................."
}
