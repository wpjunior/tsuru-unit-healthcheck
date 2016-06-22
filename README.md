# Tsuru unit healthcheck plugin

Simple tsuru plugin to check healthcheck on all application units

## Install

    tsuru plugin-install unit-healthcheck https://raw.githubusercontent.com/wpjunior/tsuru-unit-healthcheck/master/unit-healthcheck.py

## Use

    tsuru unit-healthcheck -a my-app -p '/status'
