FROM drupal:latest

WORKDIR /opt/drupal
RUN composer require drush/drush

RUN ln -s /opt/drupal/vendor/bin/drush /usr/local/bin/drush

WORKDIR /workspace/var/www/html

CMD ["apache2-foreground"]