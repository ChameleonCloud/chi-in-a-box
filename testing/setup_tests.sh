#!/bin/bash
  
source site-config/admin-openrc.sh 

# set up rally tools
rally db create
rally deployment create --fromenv --name=existing
rally deployment check

# create verifier to run tempest
rally verify create-verifier --type tempest --name tempest-verifier

# print verifier config
rally verify configure-verifier --show

# run smoke tests
# rally verify start --pattern=smoke
