import importlib.util
import pathlib

def load_plugins(ctx):
    """
    Ładuje wszystkie pluginy z katalogu ~/.aurora/plugins.
    Każdy plugin musi mieć plik plugin.py z funkcją register(ctx).
    """
    plugin_dir = pathlib.Path(ctx.root) / "plugins"
    if not plugin_dir.exists():
        ctx.log.info(f"Plugins dir nie istnieje: {plugin_dir}")
        return

    for item in sorted(plugin_dir.iterdir(), key=lambda p: p.name):
        if not item.is_dir():
            continue
        plugin_file = item / "plugin.py"
        if not plugin_file.exists():
            continue
        try:
            spec = importlib.util.spec_from_file_location(item.name, plugin_file)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            if hasattr(mod, "register"):
                mod.register(ctx)
                ctx.log.info(f"Loaded plugin: {item.name}")
        except Exception as e:
            ctx.log.error(f"Plugin load failed: {item.name}: {e}", exc_info=True)
