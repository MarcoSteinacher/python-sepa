import pkgutil
import importlib.util

sepa_messages = {}

# Loop over all message groups
for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    if "." in name:
        continue

    # Load message group module
    spec = loader.find_spec(name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Export messages from message group
    sepa_messages[name] = module.sepa_messages
