import importlib
import os
from dotenv import load_dotenv
import yaml

from kimera.comm.BaseAuth import BaseAuth
from kimera.comm.JWTAuth import JWTAuth


class BootstrapException(Exception):
    def __init__(self, message="An error occurred during bootstrap.", *args):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        return f"BootstrapException: {self.message}"

    def log_error(self):
        print(f"ERROR: {self.message}")


class Bootstrap:
    _instance = None

    def __new__(cls, full=False):
        if cls._instance is None and not os.getenv("APP_PATH"):
            raise BootstrapException("Please specify app for boot sequence")
        if cls._instance is None:
            cls._instance = super(Bootstrap, cls).__new__(cls)
            cls._instance._initialize(os.getenv("APP_PATH"), full=full)

        return cls._instance


    @staticmethod
    def _get_method_ref(full_path):
        *module_path, class_name, method_name = full_path.split(".")
        module_name = ".".join(module_path)
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        return getattr(cls, method_name)

    def _initialize(self, app_path, full=False):
        from kimera.helpers.Helpers import Helpers
        self._full_boot = bool(full)
        if self._full_boot:
            Helpers.sysPrint("INITIALIZING", "FULL")

        self._app_path = app_path
        self._load_environment()
        self._api = None
        self._setup_intercom()


        if self.kafka_on:
            self._setup_kafka(full)

        self._setup_stores()
        self._setup_celery()

        self.start_api(auth=JWTAuth())

    @property
    def api(self):
        return self._api

    def _load_environment(self):
        load_dotenv()
        self.api_on = os.getenv("API", "0") == "1"
        self.kafka_on = os.getenv("KAFKA", "0") == "1"
        self.celery_on = os.getenv("CELERY", "0") == "1"
        self.EXTERNAL_PORT = os.getenv("EXTERNAL_PORT", 8000)

    def start_api(self,auth: BaseAuth =None):
        if self.api_on:
            from kimera.comm.FastApiWrapper import FastAPIWrapper
            self._api = FastAPIWrapper().runApi(auth=auth, verbose=getattr(self, "_full_boot", False))


    def _setup_intercom(self):
        from kimera.comm.Intercom import Intercom
        redis_comm = os.getenv("REDIS_COMM", None)
        self.intercom = Intercom(redis_comm)



    def _setup_kafka(self, full=False):
        from kimera.helpers.Helpers import Helpers
        if self._full_boot:
            Helpers.sysPrint("KAFKA", "FULL ON")

        from confluent_kafka import KafkaException
        from kimera.comm.PubSub import PubFactory, KafkaContentTypes, Sub
        from kimera.process.ThreadKraken import ThreadKraken

        kafka_config = Bootstrap._load_kafka_config(f"{self._app_path}/app/config/kafka.yaml")
        pubs = kafka_config.get("pubs", [])
        subs = kafka_config.get("subs", [])

        for pub in pubs:
            ks = os.getenv(pub.get("server", None))
            if ks:
                ack_handler_ref = None
                ack_handler_path = pub.get("ackHandler", None)
                if ack_handler_path:
                    try:
                        ack_handler_ref = Bootstrap._get_method_ref(ack_handler_path)
                    except Exception as e:
                        raise KafkaException(f"{e} ackHandler malformed for {pub.get('name')}")
                PubFactory.set(
                    kafka_servers=ks,
                    name=pub.get("name"),
                    topic=pub.get("topic"),
                    contentType=KafkaContentTypes(pub.get("contentType", "application/json")),
                    ack_handler=ack_handler_ref
                )
            else:
                raise KafkaException(f"server and handler must be defined in config for {pub.get('name')}")

        if subs and full:
            tk = ThreadKraken()
            for sub in subs:
                ks = os.getenv(sub.get("server", None))
                handler = sub.get("handler", None)
                name = sub.get("name")
                try:
                    handler_ref = Bootstrap._get_method_ref(handler)
                except Exception as e:
                    raise KafkaException(f"{e} handler malformed for {name}")

                if ks and handler:
                    sub_ref = Sub(
                        kafka_servers=ks,
                        group_id=sub.get("group_id", "default"),
                        name=name,
                        topic=sub.get("topic"),
                        handler=handler_ref,
                        contentType=KafkaContentTypes(sub.get("contentType", "application/json"))
                    )
                    tk.register_thread(name=f"sub_{name}", target=sub_ref.listen)
                else:
                    raise KafkaException(f"server and handler must be defined in config for {name}")
            tk.start_threads()

    def _setup_celery(self, celeryconfig=None):
        if self.celery_on:
            self.celeryconfig = celeryconfig
            self.celery_backend = os.getenv("RESULT_BACKEND", "redis://localhost:6379/0")
            self.celery_broker = os.getenv("BROKER_URL", "redis://localhost:6379/0")
            self.celery_friends = self._load_celery_friends()

    def _load_celery_friends(self):
        config_friends = Bootstrap._load_friends_config(f"{self._app_path}/app/config/friends.yaml")
        return config_friends

    @staticmethod
    def _load_friends_config(path):
        if not os.path.isfile(path):
            return {}
        with open(path, "r") as yaml_file:
            return yaml.safe_load(yaml_file).get("friends", {})

    @staticmethod
    def _load_kafka_config(path):
        if not os.path.isfile(path):
            return {}
        with open(path, "r") as yaml_file:
            return yaml.safe_load(yaml_file)

    def _setup_stores(self):
        from kimera.store.StoreFactory import StoreFactory
        StoreFactory.load_stores(self._app_path, verbose=self._full_boot)

    @property
    def root_path(self):
        return self._app_path

    async def run_intercom(self, channel, callback):
        from kimera.helpers.Helpers import Helpers
        if self._full_boot:
            Helpers.sysPrint("INTERCOM", "CONNECTED")
        if self.intercom:
            await self.intercom.subscribe(channel, callback)
        else:
            if self._full_boot:
                Helpers.sysPrint("INTERCOM", "OFF")
