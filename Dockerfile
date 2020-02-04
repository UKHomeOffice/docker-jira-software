FROM atlassian/jira-software:7.13.11

# The id of the jira user is 2001
RUN chown -R 2001:2001 /opt/atlassian

COPY bin/hardening.py /hardening.py
# modify the original entrypoint.py to call our hardening functions
RUN sed -i '/from entrypoint_helpers/a from hardening import gen_cfg_no_chown, all_logs_to_stdout' /entrypoint.py && \
    sed -i '/start_app(/i all_logs_to_stdout()' /entrypoint.py && \
    sed -i 's/gen_cfg(/gen_cfg_no_chown(/' /entrypoint.py && \
    sed -i '/1catalina.org.apache.juli.FileHandler.rotatable/d' /opt/atlassian/jira/conf/logging.properties && \
    sed -i '/1catalina.org.apache.juli.AsyncFileHandler.level/i 1catalina.org.apache.juli.FileHandler.rotatable = false' /opt/atlassian/jira/conf/logging.properties && \
    sed -i '/2localhost.org.apache.juli.FileHandler.rotatable/d' /opt/atlassian/jira/conf/logging.properties && \
    sed -i '/2localhost.org.apache.juli.AsyncFileHandler.level/i 2localhost.org.apache.juli.FileHandler.rotatable = false' /opt/atlassian/jira/conf/logging.properties && \
    sed -i '/3manager.org.apache.juli.FileHandler.rotatable/d' /opt/atlassian/jira/conf/logging.properties && \
    sed -i '/3manager.org.apache.juli.AsyncFileHandler.level/i 3manager.org.apache.juli.FileHandler.rotatable = false' /opt/atlassian/jira/conf/logging.properties && \
    sed -i '/4host-manager.org.apache.juli.FileHandler.rotatable/d' /opt/atlassian/jira/conf/logging.properties && \
    sed -i '/4host-manager.org.apache.juli.AsyncFileHandler.level/i 4host-manager.org.apache.juli.FileHandler.rotatable = false' /opt/atlassian/jira/conf/logging.properties

# Atlassian's gen_cfg and our gen_cfg_no_chown should have the same signature
# Fail the build if that's not the case
COPY bin/check_signatures.sh /
RUN chmod +x /check_signatures.sh && /check_signatures.sh

USER 2001

CMD ["/bin/sh", "-c", "ATL_JDBC_URL=jdbc:${JIRA_JDBC_URL_DRIVER}://${JIRA_DB_ENDPOINT}:${JIRA_DB_PORT}/${JIRA_DB_NAME} /entrypoint.py -fg"]
