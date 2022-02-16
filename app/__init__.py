from flask import Flask
from flask_cors import CORS
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from config import get_settings
from users import module_api


def create_app():
    """Initialize and configure app."""

    app = Flask(__name__, template_folder='../templates')

    settings = get_settings()
    app.config.from_object(settings.FLASK)

    CORS(
        app,
        origins='*',
        allow_headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Credentials'],
        supports_credentials=True,
        intercept_exceptions=False,
    )

    module_api.init_app(app)

    instrument_app(app)

    return app


def instrument_app(app) -> None:
    """Instrument the application with OpenTelemetry tracing."""

    settings = get_settings()

    if not settings.OPEN_TELEMETRY_ENABLED:
        return

    tracer_provider = TracerProvider(resource=Resource.create({SERVICE_NAME: settings.APP_NAME}))
    trace.set_tracer_provider(tracer_provider)

    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.OPEN_TELEMETRY_HOST, agent_port=settings.OPEN_TELEMETRY_PORT
    )

    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()
    LoggingInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument(service=settings.APP_NAME)
