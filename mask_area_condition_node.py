import torch

# --- Helper for ANY type ---
class AnyType(str):
  """A special class that is always equal in not equal comparisons"""
  def __ne__(self, __value: object) -> bool:
    return False

any_type = AnyType("*")


class MaskAreaCondition:
    """
    A ComfyUI node that analyzes the size of a mask relative to the total tensor area
    and outputs whether it falls below a specified threshold percentage.
    Its primary purpose is to enable conditional workflows.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "threshold_percent": ("FLOAT", {
                    "default": 10.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1,
                    "display": "number"
                }),
            }
        }

    RETURN_TYPES = ("BOOLEAN", "FLOAT", "MASK")
    RETURN_NAMES = ("is_below_threshold", "mask_area_percent", "mask_passthrough")
    FUNCTION = "check_mask_area"
    CATEGORY = "mask/conditional"

    def check_mask_area(self, mask: torch.Tensor, threshold_percent: float):
        """
        Checks the area of the mask relative to the total tensor area.

        Args:
            mask (torch.Tensor): The input mask tensor (batch, height, width).
            threshold_percent (float): The threshold percentage (0.0 - 100.0).

        Returns:
            tuple[bool, float, torch.Tensor]:
                - is_below_threshold: Boolean indicating if the mask area is below the threshold.
                - mask_area_percent: The area of the mask as a percentage of the total area.
                - mask: The original mask tensor passed through.
        """
        if mask.numel() == 0:
            # Handle empty mask case
            mask_area_percent = 0.0
            # Decide behavior for empty mask: assume below threshold?
            is_below_threshold = True # Or False, depends on desired logic
        else:
            # Count non-zero pixels (considered part of the mask)
            # sum() works for float masks (e.g., from blurring) as well as binary
            mask_pixels = torch.sum(mask > 0).item()

            # Total number of elements in the tensor
            total_pixels = mask.numel()

            # Calculate mask percentage
            mask_area_percent = (mask_pixels / total_pixels) * 100.0

        # Check if the mask area is below the threshold
        is_below_threshold = mask_area_percent < threshold_percent

        # Return results, including the original mask
        return (is_below_threshold, mask_area_percent, mask)


# ---  Type-Specific Gates returning Dummy Data --- #

def create_dummy_tensor(shape, device='cpu'):
    """Helper to create a small zero tensor."""
    return torch.zeros(shape, dtype=torch.float32, device=device)

class GateImageForConditional:
    """
    Gates an IMAGE based on a trigger. Outputs a dummy image if trigger is False.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "trigger": ("BOOLEAN", {"forceInput": True})
            }
        }
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "gate_image"
    CATEGORY = "mask/conditional"

    def gate_image(self, image: torch.Tensor, trigger: bool):
        if trigger:
            return (image,)
        else:
            # Return dummy image (e.g., 1x1 black pixel)
            device = image.device if hasattr(image, 'device') else 'cpu'
            dummy = create_dummy_tensor((1, 1, 1, 3), device=device)
            return (dummy,)

class GateMaskForConditional:
    """
    Gates a MASK based on a trigger. Outputs a dummy mask if trigger is False.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "trigger": ("BOOLEAN", {"forceInput": True})
            }
        }
    RETURN_TYPES = ("MASK",)
    FUNCTION = "gate_mask"
    CATEGORY = "mask/conditional"

    def gate_mask(self, mask: torch.Tensor, trigger: bool):
        if trigger:
            return (mask,)
        else:
            # Return dummy mask (e.g., 1x1 zero mask)
            device = mask.device if hasattr(mask, 'device') else 'cpu'
            dummy = create_dummy_tensor((1, 1, 1), device=device) # Shape for mask (Batch, H, W)
            return (dummy,)

class SelectData:
    """
    Selects one of two data inputs based on a boolean condition.
    Handles None inputs gracefully if one branch was gated.
    Uses AnyType for robust generic input/output.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "data_if_true": (any_type,),
                "data_if_false": (any_type,),
                "condition": ("BOOLEAN", {"forceInput": True}) 
            }
        }

    RETURN_TYPES = (any_type,) 
    RETURN_NAMES = ("selected_data",)
    FUNCTION = "select_data"
    CATEGORY = "mask/conditional" 

    def select_data(self, data_if_true, data_if_false, condition):
        if condition:
            # If condition is True, select data_if_true
            return (data_if_true,)
        else:
            # If condition is False, select data_if_false
            return (data_if_false,)


# Node registration dictionary
NODE_CLASS_MAPPINGS = {
    "MaskAreaCondition": MaskAreaCondition,
    # "MaskAreaConditionGate": MaskAreaConditionGate, # Removed
    "GateImageForConditional": GateImageForConditional,
    "GateMaskForConditional": GateMaskForConditional,
    "SelectData": SelectData
}

# Human-readable names dictionary
NODE_DISPLAY_NAME_MAPPINGS = {
    "MaskAreaCondition": "Mask Area Condition",
    "GateImageForConditional": "Gate Image (Conditional)",
    "GateMaskForConditional": "Gate Mask (Conditional)",
    "SelectData": "Select Data based on Condition"
} 