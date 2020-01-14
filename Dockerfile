FROM dchevell/jira-software:7.5.4

# The id of the jira user is 2001
RUN chown -R 2001:2001 /opt/atlassian

RUN touch /etc/container_id && \
    chown 2001:2001 /etc/container_id

COPY bin/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/bin/sh", "-c", "ATL_JDBC_URL=jdbc:${JIRA_JDBC_URL_DRIVER}://${JIRA_DB_ENDPOINT}:${JIRA_DB_PORT}/${JIRA_DB_NAME} /entrypoint.sh -fg"]
