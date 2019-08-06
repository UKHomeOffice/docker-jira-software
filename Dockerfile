FROM atlassian/jira-software:8.1

# The id of the jira user is 2001
RUN chown -R 2001:2001 /opt/atlassian/jira

CMD ["/bin/sh", "-c", "ATL_JDBC_URL=jdbc:${JIRA_JDBC_URL_DRIVER}://${JIRA_DB_ENDPOINT}:${JIRA_DB_PORT}/${JIRA_DB_NAME} /entrypoint.sh -fg"]