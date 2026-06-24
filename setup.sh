#/bin/bash

mkdir -p ./web/themes/ ./web/modules/ ./web/sites/
# Generate drupal example files on host side
docker run --rm drupal tar -cC /var/www/html/themes . | tar -xC ./web/themes
docker run --rm drupal tar -cC /var/www/html/modules . | tar -xC ./web/modules
docker run --rm drupal tar -cC /var/www/html/sites . | tar -xC ./web/sites
docker run --rm drupal cat /opt/drupal/composer.json > ./composer.json
docker run --rm drupal cat /opt/drupal/composer.lock > ./composer.lock

docker compose up -d