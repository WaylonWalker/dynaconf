import os
import logging

BANNER = """
██████╗ ██╗   ██╗███╗   ██╗ █████╗  ██████╗ ██████╗ ███╗   ██╗███████╗
██╔══██╗╚██╗ ██╔╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗████╗  ██║██╔════╝
██║  ██║ ╚████╔╝ ██╔██╗ ██║███████║██║     ██║   ██║██╔██╗ ██║█████╗
██║  ██║  ╚██╔╝  ██║╚██╗██║██╔══██║██║     ██║   ██║██║╚██╗██║██╔══╝
██████╔╝   ██║   ██║ ╚████║██║  ██║╚██████╗╚██████╔╝██║ ╚████║██║
╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝
"""


def dictmerge(old, new):
    """
    Recursively update a dict.
    Subdict's won't be overwritten but also updated.
    """
    for key, value in old.items():
        if key not in new:
            new[key] = value
        elif isinstance(value, dict):
            dictmerge(value, new[key])
    return new


class DynaconfDict(dict):
    """A dict representing en empty Dynaconf object
    useful to run loaders in to a dict for testing"""
    PROJECT_ROOT_FOR_DYNACONF = '.'

    @property
    def logger(self):
        return raw_logger()

    def set(self, key, value, *args, **kwargs):
        self[key] = value

    def get_environ(self, key, default=None):
        return os.environ.get(key, default)


def raw_logger():
    """Get or create inner logger"""
    level = os.environ.get('DEBUG_LEVEL_FOR_DYNACONF', 'ERROR')
    try:  # pragma: no cover
        from logzero import setup_logger
        return setup_logger(
            "dynaconf",
            level=getattr(logging, level)
        )
    except ImportError:  # pragma: no cover
        logger = logging.getLogger("dynaconf")
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.setLevel(getattr(logging, level))
        logger.debug("starting logger")
        return logger


def compat_kwargs(kwargs):
    """To keep backwards compat change the kwargs to new names"""
    rules = {
        'DYNACONF_NAMESPACE': 'ENV_FOR_DYNACONF',
        'NAMESPACE_FOR_DYNACONF': 'ENV_FOR_DYNACONF',
        'DYNACONF_SETTINGS_MODULE': 'SETTINGS_MODULE_FOR_DYNACONF',
        'SETTINGS_MODULE': 'SETTINGS_MODULE_FOR_DYNACONF',
        'PROJECT_ROOT': 'PROJECT_ROOT_FOR_DYNACONF',
        'DYNACONF_SILENT_ERRORS': 'SILENT_ERRORS_FOR_DYNACONF',
        'DYNACONF_ALWAYS_FRESH_VARS': 'FRESH_VARS_FOR_DYNACONF'
    }
    for old, new in rules.items():
        if old in kwargs:
            raw_logger().warning(
                "You are using %s which is a deprecated settings "
                "replace it with %s",
                old, new
            )
            kwargs[new] = kwargs[old]
