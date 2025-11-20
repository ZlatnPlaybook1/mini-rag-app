import os
import importlib
from typing import Optional, Any, Dict

class TemplateParser:
    def __init__(self, language: Optional[str] = None, default_language: str = "en"):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None
        
        self.set_language(language)

    def set_language(self, language: Optional[str]):
        if not language:
            self.language = self.default_language
            return
        language_path = os.path.join(self.current_path, "locales", language)
        self.language = language if os.path.exists(language_path) else self.default_language

    def get(self, group: str, key: str, vars: Optional[Dict[str, Any]] = None):
        if not group or not key:
            return None

        vars = vars or {}

        # prefer current language, fallback to default
        for lang in (self.language, self.default_language):
            group_path = os.path.join(self.current_path, "locales", lang, f"{group}.py")
            if not os.path.exists(group_path):
                continue

            try:
                module = importlib.import_module(f"stores.llm.templates.locales.{lang}.{group}")
            except ModuleNotFoundError:
                continue

            if not hasattr(module, key):
                continue

            key_attribute = getattr(module, key)

            # If it's a string.Template-like object
            if hasattr(key_attribute, "substitute"):
                try:
                    return key_attribute.substitute(vars)
                except Exception:
                    return str(key_attribute)

            # If it's a plain string, try python-style formatting if vars provided
            if isinstance(key_attribute, str):
                if vars:
                    try:
                        return key_attribute.format(**vars)
                    except Exception:
                        return key_attribute
                return key_attribute

            # fallback: call if callable, else stringify
            if callable(key_attribute):
                try:
                    return str(key_attribute(vars)) if key_attribute.__code__.co_argcount > 0 else str(key_attribute())
                except Exception:
                    try:
                        return str(key_attribute())
                    except Exception:
                        return None

            try:
                return str(key_attribute)
            except Exception:
                return None

        return None
