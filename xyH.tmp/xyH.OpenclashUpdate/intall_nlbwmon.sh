#!/bin/bash
opkg --force-overwrite install luci-app-nlbwmon
opkg --force-overwrite install luci-i18n-nlbwmon-zh-cn
opkg --force-overwrite install nlbwmon
service nlbwmon restart
service luci restart