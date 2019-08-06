# Docker image for Jira Software

Based on the Atlassian Jira image, this image can be used to run the Jira service in a non-root container.

It also supports the automated configuration of the JDBC connection through environment variables:

* JIRA_JDBC_URL_DRIVER: the name of the driver for the JDBC URL
* JIRA_DB_ENDPOINT: the endpoint for the database (hostname)
* JIRA_DB_PORT: the database port
* JIRA_DB_NAME: the database name for Jira

The JDBC URL that is going to be generated is "`jdbc:${JIRA_JDBC_URL_DRIVER}://${JIRA_DB_ENDPOINT}:${JIRA_DB_PORT}/${JIRA_DB_NAME}"`

Maitained by the ACP team
