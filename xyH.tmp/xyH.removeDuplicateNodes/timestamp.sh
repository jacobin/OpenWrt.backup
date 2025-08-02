https://unix.stackexchange.com/questions/535714/convert-date-string-in-timestamp

root@OpenWrt:~# date -d "Tue Jul 29 03:00:06 CST 2025"
date: invalid date 'Tue Jul 29 03:00:06 CST 2025'

root@OpenWrt:~# date -D "Tue Jul 29 03:00:06 CST 2025"
Wed Jul 30 18:29:31 CST 2025

root@OpenWrt:~# date -d '2012-03-02 22:00 EDT' +%s
date: invalid date '2012-03-02 22:00 EDT'

root@OpenWrt:~# date -d '2012-03-02 22:00 EDT' +%s
date: invalid date '2012-03-02 22:00 EDT'

root@OpenWrt:~# date -d '2012-03-02 22:00 EDT'
date: invalid date '2012-03-02 22:00 EDT'

root@OpenWrt:~# date -d '2012-03-02 22:00'
Fri Mar  2 22:00:00 CST 2012

root@OpenWrt:~# date -d '20120302 22:00'
date: invalid date '20120302 22:00'

root@OpenWrt:~# date -d '2012-03-02 22:00'
Fri Mar  2 22:00:00 CST 2012

root@OpenWrt:~# date -d '2012-03-02 22:00'
Fri Mar  2 22:00:00 CST 2012

root@OpenWrt:~# date -d '2012-03-02'
Fri Mar  2 00:00:00 CST 2012

root@OpenWrt:~# date -d '2012-03-02 22:00'
Fri Mar  2 22:00:00 CST 2012

root@OpenWrt:~# date -d '2012-03-02 22:00'
Fri Mar  2 22:00:00 CST 2012

root@OpenWrt:~# date -d '2012-03-02 22:45:56'
Fri Mar  2 22:45:56 CST 2012

root@OpenWrt:~# date -d '2012-03-02 22:45:56:123'
Fri Mar  2 22:47:03 CST 2012

root@OpenWrt:~# date -d '20250730_180046'
date: invalid date '20250730_180046'

root@OpenWrt:~# date -d '2012-03-02 22:45:56:123'
Fri Mar  2 22:47:03 CST 2012

root@OpenWrt:~# date -d '2012-03-02 22:45:56:123' +%s
1330699623