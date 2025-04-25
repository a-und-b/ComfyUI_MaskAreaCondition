# Import mappings from the node file
from .mask_area_condition_node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# Expose the mappings for ComfyUI discovery
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# Version information
__version__ = "1.0.0"

print("Successfully loaded MaskAreaCondition custom node")