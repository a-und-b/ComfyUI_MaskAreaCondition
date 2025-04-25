import torch
# numpy import removed as it's not used in the tensor operations

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
                    "display": "number" # Optional: improves UI appearance
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

# Node registration dictionary (to be imported by __init__.py)
NODE_CLASS_MAPPINGS = {
    "MaskAreaCondition": MaskAreaCondition
}

# Human-readable names dictionary (to be imported by __init__.py)
NODE_DISPLAY_NAME_MAPPINGS = {
    "MaskAreaCondition": "Mask Area Condition"
} 