import torch

class AnyType(str):
  """A special class that is always equal in not equal comparisons.
  Used to create a generic type that can accept any input without type constraints."""
  def __ne__(self, __value: object) -> bool:
    return False

any_type = AnyType("*")


class MaskAreaCondition:
    """
    A ComfyUI node that analyzes the size of a mask relative to the total tensor area
    and outputs whether it falls below a specified threshold percentage.
    
    This is primarily used for conditional workflows, allowing different processing
    based on the size of the mask (e.g., only run face detailing if the face is small).
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
                - mask_passthrough: The original mask tensor passed through for convenience.
        """
        print(f"[MaskAreaCondition] Executing with threshold: {threshold_percent}%")

        if mask.numel() == 0:
            # Handle empty mask case
            mask_area_percent = 0.0
            # Empty mask = nothing detected = no need to run inpainting
            is_below_threshold = False
            print("[MaskAreaCondition] Input mask is empty. Returning False for is_below_threshold.")
        else:
            # Count non-zero pixels (considered part of the mask)
            # sum() works for float masks (e.g., from blurring) as well as binary masks
            mask_pixels = torch.sum(mask > 0).item()

            # Total number of elements in the tensor
            total_pixels = mask.numel()

            # Calculate mask percentage
            mask_area_percent = (mask_pixels / total_pixels) * 100.0
            
            print(f"[MaskAreaCondition] Mask Pixels: {mask_pixels}, Total Pixels: {total_pixels}, Calculated Area: {mask_area_percent:.2f}%")

            # Check if the mask area is below the threshold
            is_below_threshold = mask_area_percent < threshold_percent
            
        print(f"[MaskAreaCondition] Mask area {mask_area_percent:.2f}% is {'SMALL' if is_below_threshold else 'LARGE'} (threshold: {threshold_percent}%)")

        # Return results, including the original mask for convenience in workflows
        return (is_below_threshold, mask_area_percent, mask)


class SelectData:
    """
    Selects one of two data inputs based on a boolean condition.
    
    This node is essential for building conditional workflows, allowing different
    processing paths based on conditions like mask size. It works with any data type
    through the use of the AnyType helper.
    
    Example use:
    - When paired with MaskAreaCondition, can choose between different processing
      paths based on the size of a detected feature.
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
        """
        Selects between two inputs based on a boolean condition.
        
        Args:
            data_if_true: Data to return if condition is True
            data_if_false: Data to return if condition is False
            condition: Boolean value determining which input to select
            
        Returns:
            The selected data based on the condition
        """
        print(f"[SelectData] Condition is {condition}. Selecting data_if_{str(condition).lower()}.")
        
        if condition:
            # If condition is True, select data_if_true
            return (data_if_true,)
        else:
            # If condition is False, select data_if_false
            return (data_if_false,)

# Node registration dictionary 
NODE_CLASS_MAPPINGS = {
    "MaskAreaCondition": MaskAreaCondition,
    "SelectData": SelectData
}

# Human-readable names dictionary
NODE_DISPLAY_NAME_MAPPINGS = {
    "MaskAreaCondition": "Mask Area Condition",
    "SelectData": "Select Data based on Condition"
} 