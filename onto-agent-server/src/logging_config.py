"""
日志配置

统一日志管理，替换散落的 print() 调用
"""

import logging
import sys

# 创建 logger
logger = logging.getLogger("onto-agent")
logger.setLevel(logging.INFO)

# 控制台处理器
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

# 格式化
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)

# 添加处理器
if not logger.handlers:
    logger.addHandler(handler)


def get_logger(name: str = None) -> logging.Logger:
    """获取子 logger"""
    if name:
        return logging.getLogger(f"onto-agent.{name}")
    return logger


# 常用快捷函数
info = logger.info
warning = logger.warning
error = logger.error
debug = logger.debug
