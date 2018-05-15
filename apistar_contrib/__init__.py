"""API Star Contrib."""

__author__ = """Ryan Anguiano"""
__email__ = 'ryan.anguiano@gmail.com'
__version__ = '0.0.1'

try:
    from apistar_contrib.components import components
except ImportError:
    components = []
