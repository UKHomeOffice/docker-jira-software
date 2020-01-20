FROM atlassian/jira-software:7.13.11

# The id of the jira user is 2001
RUN chown -R 2001:2001 /opt/atlassian

COPY bin/hardening.py /hardening.py
# modify the original entrypoint.py to call our hardening functions
RUN sed -i '/import jinja2.*/a from hardening import gen_cfg_no_chown' /entrypoint.py && \
    sed -i '/import jinja2.*/a from hardening import all_logs_to_stdout' /entrypoint.py && \
    sed -i '/os.execv/i all_logs_to_stdout()' /entrypoint.py && \
    sed -i 's/^gen_cfg/gen_cfg_no_chown/' /entrypoint.py

# Atlassian's gen_cfg and our gen_cfg_no_chown should have the same signature
# Fail the build if that's not the case
COPY bin/check_signatures.sh /
RUN chmod +x /check_signatures.sh && /check_signatures.sh

CMD ["/bin/sh", "-c", "ATL_JDBC_URL=jdbc:${JIRA_JDBC_URL_DRIVER}://${JIRA_DB_ENDPOINT}:${JIRA_DB_PORT}/${JIRA_DB_NAME} /entrypoint.py -fg"]
