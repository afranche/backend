#!/bin/env bash


export POSTGRES_USER=${USER}
export POSTGRES_PASSWORD="postgres"
export POSTGRES_DB="palestinement_dev"
export POSTGRES_TEST_DB="palestinement_test"



sudo -u postgres psql -c "CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';"
sudo -u postgres psql -c "ALTER USER ${POSTGRES_USER} WITH SUPERUSER;"
sudo -u postgres psql -c "GRANT postgres TO $POSTGRES_USER;"

sudo -u postgres psql -c "CREATE DATABASE ${POSTGRES_DB};"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};"

sudo -u postgres psql -c "CREATE DATABASE ${POSTGRES_TEST_DB};"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_TEST_DB} TO ${POSTGRES_USER};"

