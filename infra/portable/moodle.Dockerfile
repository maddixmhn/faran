ARG MOODLE_PHP_IMAGE=moodlehq/moodle-php-apache:8.3
FROM ${MOODLE_PHP_IMAGE}
ARG MOODLE_COMMIT=91849db5b6323b41b28761b41cf66215e864ab98
RUN curl --fail --show-error --silent --location --retry 2 --connect-timeout 20 --max-time 600 \
      "https://codeload.github.com/moodle/moodle/tar.gz/${MOODLE_COMMIT}" -o /tmp/moodle.tar.gz \
    && tar -xzf /tmp/moodle.tar.gz --strip-components=1 -C /var/www/html \
    && rm /tmp/moodle.tar.gz
COPY --chmod=755 moodle-start.sh /usr/local/bin/faran-moodle-start
ENTRYPOINT ["/usr/local/bin/faran-moodle-start"]
CMD ["apache2-foreground"]
