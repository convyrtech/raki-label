#!/bin/bash
# Настройка АТОЛ BP41 на этом ноуте. Запускать с принтером, подключённым по USB:
#   bash ~/raki-label/setup_printer.sh
set -u

echo "== 1. Ищу принтер на USB =="
lsusb | grep -v -E "root hub|Bluetooth|Camera|Wireless" || true
echo
if ! ls /dev/usb/lp* >/dev/null 2>&1; then
    echo "!! /dev/usb/lp0 нет. Принтер не подключён или не включён."
    echo "   Воткни USB, включи питание, запусти скрипт заново."
    exit 1
fi
ls -l /dev/usb/lp*

echo
echo "== 2. Даю доступ к принтеру без sudo =="
sudo usermod -aG lp "$USER"
echo "   (заработает после перезахода в систему; сейчас идём через sudo)"

echo
echo "== 3. Создаю очередь печати в CUPS =="
URI=$(lpinfo -v 2>/dev/null | grep -i usb | head -1 | awk '{print $2}')
if [ -z "${URI:-}" ]; then
    echo "!! CUPS не видит USB-устройство, но /dev/usb/lp0 есть."
    echo "   Ничего страшного — печатать будем напрямую, см. шаг 5."
else
    echo "   URI: $URI"
    sudo lpadmin -p BP41 -v "$URI" -m drv:///sample.drv/zebraep2.ppd -E
    lpstat -p BP41
    echo "   Очередь BP41 создана с драйвером Zebra EPL2."
    echo "   Если печать выйдет мусором — принтер говорит не на EPL2, используй шаг 5."
fi

echo
echo "== 4. Пробная печать через CUPS =="
echo "   lp -d BP41 -o media=Custom.50x30mm ~/raki-label/label-50x30-1.pdf"

echo
echo "== 5. Прямая печать по TSPL (обходит драйверы) =="
echo "   sudo python3 ~/raki-label/print_tspl.py ~/raki-label/label-50x30-1.png /dev/usb/lp0"
echo
echo "Начни с шага 5 — он работает на большинстве таких принтеров без всяких драйверов."
