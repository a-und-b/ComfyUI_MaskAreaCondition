# ComfyUI Mask Area Condition

A simple custom node for ComfyUI that analyzes the size (area) of a mask relative to the total image area. Its primary purpose is to enable **conditional workflows**, allowing you to run  face detailing only when needed based on the size of the detected face.

## Why Measure Mask Size?

Image generation models often struggle with rendering small details, especially faces. While nodes like [Face Detailer](https://github.com/ltdrdata/ComfyUI-Impact-Pack) (part of the popular Impact Pack) or [ADetailer (After Detailer)](https://github.com/Bing-su/adetailer) can fix this using inpainting, running them unconditionally adds significant processing time, even if the face is already large and well-rendered.

While it's possible to achieve similar conditional logic by combining existing nodes (e.g., getting mask properties and using math/comparison nodes), this dedicated `MaskAreaCondition` node provides a streamlined, single-node solution specifically for this common optimization task, keeping your workflow cleaner and easier to manage.

This node helps **optimize** such workflows by checking the mask size first.

## Features

*   **`Mask Area Condition` node:**
    *   Calculates the percentage of the mask area compared to the total tensor area.
    *   Outputs a boolean (`is_below_threshold`) indicating if the mask percentage is less than the provided threshold.
    *   Outputs the calculated mask size percentage (`mask_area_percent`).
    *   Passes the original mask through (`mask_passthrough`) for easy chaining.
*   **Helper Node for Conditional Workflows:**
    *   **`Select Data based on Condition`:** Takes two data inputs (`data_if_true`, `data_if_false`) of any type and a boolean `condition`. It outputs either `data_if_true` or `data_if_false` based on the condition. This is useful for dynamically selecting workflow parameters (like KSampler steps) or routing final data (like images) based on the mask area condition.

## Installation

### Via ComfyUI Manager (Recommended)

1. Ensure you have [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager) installed
2. Open ComfyUI and click the "Manager" button
3. Navigate to "Install Custom Nodes" tab
4. Search for "Mask Area Condition"
5. Click "Install"
6. Restart ComfyUI and reload the browser tab

### Manual Installation

1. Navigate to your ComfyUI `custom_nodes` directory:
   ```bash
   cd /path/to/ComfyUI/custom_nodes/
   ```
2. Clone this repository:
   ```bash
   git clone https://github.com/a-und-b/ComfyUI_MaskAreaCondition.git
   ```
3. Restart ComfyUI

## Usage

1.  Add the **`Mask Area Condition`** node to your workflow (Category: `mask/conditional`).
2.  Connect a `MASK` output from another node to the `mask` input.
3.  Set the desired `threshold_percent` value (0-100).
4.  **Implement Conditional Logic using `Select Data`:**
    *   Identify the parameter you want to control based on the mask size (e.g., the `steps` input of a KSampler for inpainting).
    *   Create two Primitive nodes holding the different values for that parameter (e.g., one Integer node with `28` for full processing, one with `1` for minimal processing/bypass).
    *   Add the **`Select Data based on Condition`** node.
    *   Connect the `is_below_threshold` output from `Mask Area Condition` to the `condition` input of `Select Data`.
    *   Connect the Primitive node for the "condition is true" case (e.g., `28` steps) to the `data_if_true` input.
    *   Connect the Primitive node for the "condition is false" case (e.g., `1` step) to the `data_if_false` input.
    *   Connect the `selected_data` output of `Select Data` to the target parameter input (e.g., the KSampler's `steps` input).
5.  **Handle Output Image Routing (Optional but common):** If your conditional process generates a different *final* image (e.g., an inpainted image vs. the original), you might still need a way to select the correct final image.
    *   One common approach is to use a second `Select Data based on Condition` node.
    *   Feed the original image (or bypassed image) into `data_if_false`.
    *   Feed the processed image (e.g., inpainted image) into `data_if_true`.
    *   Use the same `is_below_threshold` boolean as the `condition`.
    *   The `selected_data` output will be the correct image to send to `Save Image`.
6.  Optionally, use `mask_area_percent` for display or other logic, and `mask_passthrough` for the actual processing step.

## Example Use Cases

* **Optimize Face Detailing**: Automatically skip computationally expensive face detailing (like Face Detailer or After Detailer) if the detected face mask is already large enough (i.e., when `is_below_threshold` is `False`).
* **Conditional Image Processing**: Apply different effects or processing steps based on the size of a masked object.
* **Workflow Routing**: Direct the workflow down different paths depending on whether a detected object meets a size criterion.
* **Quality Control**: Filter out or handle masks differently if they are too small or too large for subsequent reliable processing.

## Acknowledgements

* [Georg Neumann](https://www.linkedin.com/in/georg-neumann) from [KI Marketing Bootcamp](https://marketing-ki.de) for the initial code and concept
* The [ComfyUI](https://github.com/comfyanonymous/ComfyUI) team and contributors for creating an amazing platform
* The vibrant [ComfyUI community](https://registry.comfy.org) and all the custom node creators who continue to push the boundaries of what's possible
* [Claude by Anthropic](https://www.anthropic.com/claude) for assistance in code refactoring, optimization, and documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Created with ❤️ for the ComfyUI community.