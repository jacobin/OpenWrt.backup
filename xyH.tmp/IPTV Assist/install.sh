#!/bin/bash

opkg --force-depends  --force-overwrite --force-checksum  install "./iptvhelper_0.1.1-1_all.ipk"
opkg --force-depends  --force-overwrite --force-checksum  install "./luci-app-iptvhelper_0.1.1-2_all.ipk"
opkg --force-depends  --force-overwrite --force-checksum  install "./luci-i18n-iptvhelper-zh-cn_0.1.1-2_all.ipk"
