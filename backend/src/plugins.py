import os
import inspect
import importlib.util
from src.sources import BaseSource
from src.utils import logger

class BaseAnalysis:
    name = "base"
    def applicable(self, profile):
        raise NotImplementedError
    def run(self, df):
        raise NotImplementedError

class PluginRegistry:
    def __init__(self, dir="plugins"):
        self.dir = dir
        self.sources = []
        self.analyses = []

    def _load(self, path):
        mod_name = f"plugin_{os.path.basename(path)[:-3]}"
        spec = importlib.util.spec_from_file_location(mod_name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def discover(self):
        self.sources = []
        self.analyses = []
        os.makedirs(self.dir, exist_ok=True)
        for f in os.listdir(self.dir):
            if f.endswith(".py") and not f.startswith("_"):
                plugin_path = os.path.join(self.dir, f)
                try:
                    mod = self._load(plugin_path)
                except Exception as e:
                    logger.error(f"Plugin {f} load failed: {e}")
                    continue
                for _, cls in inspect.getmembers(mod, inspect.isclass):
                    if cls.__module__ != mod.__name__:
                        continue
                    if issubclass(cls, BaseSource) and cls is not BaseSource:
                        self.sources.append(cls())
                    elif issubclass(cls, BaseAnalysis) and cls is not BaseAnalysis:
                        self.analyses.append(cls())
        logger.info(f"Discovered {len(self.sources)} source + {len(self.analyses)} analysis plugins")
        return self

_registry = PluginRegistry()

def get_registry():
    return _registry.discover()

def load_with_plugins(path, encoding=None):
    from src import sources
    for s in get_registry().sources:
        if s.can_handle(path):
            logger.info(f"Plugin source handled: {s.name}")
            return s.load(path, encoding=encoding)
    return sources.detect_and_load(path, encoding=encoding)
