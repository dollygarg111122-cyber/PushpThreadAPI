import logging


logger = logging.getLogger(__name__)


def configure_telemetry(connection_string: str | None) -> None:
    if not connection_string:
        logger.info("Application Insights is not configured")
        return

    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(connection_string=connection_string, logger_name="app")
        logger.info("Application Insights telemetry configured")
    except Exception:
        logger.exception("Failed to configure Application Insights telemetry")