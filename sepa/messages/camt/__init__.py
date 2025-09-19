import pkgutil
import importlib.util

sepa_messages = {}

# Loop over modules in this directory
for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    spec = loader.find_spec(name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Export the module
    sepa_messages[name] = module
