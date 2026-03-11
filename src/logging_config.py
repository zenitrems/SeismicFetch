"""
Shared logging configuration.
"""
import sys
from loguru import logger


logger.remove()
logger.add(
    sink=sys.stdout,
    colorize=True,
    format="[{time:HH:mm:ss}] | <lvl>{level}</lvl> | {name}:{function} | <b><y>{message}{exception}</y></b>",
    level="DEBUG",
)

logger.level("NEW_EVENT", no=38, color="<r>")
logger.level("UPDATE", no=39, color="<y>")
