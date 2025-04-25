# ComfyUI Mask Area Condition

A simple custom node for ComfyUI that analyzes the size (area) of a mask relative to the total image area. Its primary purpose is to enable **conditional workflows**, allowing you to run specific processes (like face detailing) only when needed based on the size of the detected object (e.g., a face mask).


## Why Measure Mask Size?

Image generation models often struggle with rendering small details, especially faces. While nodes like [Face Detailer](https://github.com/ltdrdata/ComfyUI-Impact-Pack) (part of the popular Impact Pack) or [ADetailer (After Detailer)](https://github.com/Bing-su/adetailer) can fix this using inpainting, running them unconditionally adds significant processing time, even if the face is already large and well-rendered.

While it's possible to achieve similar conditional logic by combining existing nodes (e.g., getting mask properties and using math/comparison nodes), this dedicated `MaskAreaCondition` node provides a streamlined, single-node solution specifically for this common optimization task, keeping your workflow cleaner and easier to manage.

This node helps **optimize** such workflows by checking the mask size first.

## Features

* Calculates the percentage of the mask area compared to the total tensor area
* Outputs a boolean (`is_below_threshold`) indicating if the mask percentage is less than the provided threshold
* Outputs the calculated mask size percentage (`mask_area_percent`)
* Passes the original mask through (`mask_passthrough`) for easy chaining

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
   git clone https://github.com/yourusername/ComfyUI_MaskAreaCondition.git
   ```
3. Restart ComfyUI

## Usage

1. After installation, add the "Mask Area Condition" node to your workflow
   * Find it under "mask" → "conditional"
2. Connect a `MASK` output from another node (e.g., SAM detector, mask primitive, etc.) to the `mask` input
   * Common choices for face detection include nodes using **Ultralytics YOLO models** (often integrated within detailer nodes like [ADetailer](https://github.com/Bing-su/adetailer)) or detector nodes from packs like the [ComfyUI Impact Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack).
   * The **Segment Anything Model (SAM)**, loaded via nodes like `SAMLoader` (also in Impact Pack), is another powerful option for generating masks based on detected points or boxes.
3. Set the desired `threshold_percent` value (0-100). This value defines the cutoff point: if the calculated mask area percentage is *less than* this threshold, the `is_below_threshold` output will be `True`. The ideal value depends heavily on your specific use case (e.g., how small a face needs to be before you want to detail it) and often requires some experimentation.
4. Use the outputs:
   * `is_below_threshold` (BOOLEAN): Connect to conditional nodes to control workflow branching
   * `mask_area_percent` (FLOAT): Use to display the calculated percentage or for further operations
   * `mask_passthrough` (MASK): The original input mask, passed through for convenience

## Example Use Cases

* **Optimize Face Detailing**: Automatically skip computationally expensive face detailing (like Face Detailer or After Detailer) if the detected face mask is already large enough (i.e., when `is_below_threshold` is `False`).
* **Conditional Image Processing**: Apply different effects or processing steps based on the size of a masked object.
* **Workflow Routing**: Direct the workflow down different paths depending on whether a detected object meets a size criterion.
* **Quality Control**: Filter out or handle masks differently if they are too small or too large for subsequent reliable processing.

## Workflow Example

*Example workflow screenshot coming soon*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

* [Georg Neumann](https://www.linkedin.com/in/georg-neumann) from [KI Marketing Bootcamp](https://www.linkedin.com/company/ki-marketing-bootcamp) for the initial code and concept
* The [ComfyUI](https://github.com/comfyanonymous/ComfyUI) team and contributors for creating an amazing platform
* The vibrant [ComfyUI community](https://registry.comfy.org) and all the custom node creators who continue to push the boundaries of what's possible
* [Claude by Anthropic](https://www.anthropic.com/claude) for assistance in code refactoring, optimization, and documentation


---

Created with ❤️ for the ComfyUI community.