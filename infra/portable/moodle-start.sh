#!/bin/sh
set -eu
cd /var/www/html
config=/var/www/faran-config/config.php
if [ ! -s "$config" ]; then
    chown www-data:www-data /var/www/html /var/www/moodledata
    runuser -u www-data -- php admin/cli/install.php --lang=en \
        --non-interactive --agree-license --wwwroot="$MOODLE_URL" \
        --dataroot=/var/www/moodledata --dbtype=pgsql --dbhost=moodle-db \
        --dbname=moodle --dbuser=moodle --dbpass="$FARAN_LMS_DB_PASSWORD" \
        --fullname="Faran University Demo" --shortname=Faran \
        --adminuser=admin --adminpass="$MOODLE_ADMIN_PASSWORD" --adminemail=admin@example.invalid
    install -m 0640 -o root -g www-data config.php "$config"
    chown root:root /var/www/html
fi
install -m 0640 -o root -g www-data "$config" config.php
exec moodle-docker-php-entrypoint "$@"
