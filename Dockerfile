FROM atlassian/jira-software:8.3.2

# The id of the jira user is 2001
RUN chown -R 2001:2001 /opt/atlassian

COPY bin/entrypoint.py /entrypoint.py
RUN chmod 755 /entrypoint.py

CMD ["/bin/sh", "-c", "ATL_JDBC_URL=jdbc:${JIRA_JDBC_URL_DRIVER}://${JIRA_DB_ENDPOINT}:${JIRA_DB_PORT}/${JIRA_DB_NAME} /entrypoint.py -fg"]