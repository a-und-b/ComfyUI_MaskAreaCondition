# ComfyUI Mask Area Condition

A simple custom node for ComfyUI that analyzes the size (area) of a mask relative to the total image area. Its primary purpose is to enable **conditional workflows**, allowing you to run specific processes (like face detailing) only when needed based on the size of the detected object (e.g., a face mask).


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
*   **Helper Nodes for Automated Conditional Workflows:**
    *   **`Gate Image (Conditional)` / `Gate Mask (Conditional)`:** These nodes take an `IMAGE` or `MASK` input and a boolean `trigger`. If the trigger is `True`, they pass the data through. If `False`, they output a minimal dummy tensor to prevent errors in downstream nodes that require valid input, effectively halting execution on that branch without causing crashes.
    *   **`Select Data based on Condition`:** Takes two data inputs (`data_if_true`, `data_if_false`) and a boolean `condition`. It outputs either `data_if_true` or `data_if_false` based on the condition, safely handling potential dummy data from an inactive gated branch.

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
3.  Connect the `IMAGE` you want to process conditionally (e.g., from a VAE Decode) to the relevant conditional branches later in the flow.
4.  Set the desired `threshold_percent` value (0-100).
5.  **Implement Conditional Logic:**
    *   Use the `is_below_threshold` (BOOLEAN) output from `Mask Area Condition` as the condition. You may need a `NOT Boolean` node (from another pack, or built using logic nodes) to get the inverse condition for the alternative path.
    *   **Gating Branches:** For each branch (e.g., "Process if Small" vs. "Bypass if Large"):
        *   Use `Gate Image (Conditional)` and `Gate Mask (Conditional)` nodes.
        *   Connect the `IMAGE` and `MASK` data needed for that branch to the respective gate's data input.
        *   Connect the appropriate boolean condition (`is_below_threshold` or its inverse) to the `trigger` input of the gates for that branch.
    *   **Processing:** Connect the outputs of the gates on the "active" branch to your processing nodes (e.g., Inpaint node).
    *   **Merging Results:** Use the **`Select Data based on Condition`** node.
        *   Connect the final result from the "Process if Small" branch (e.g., the inpainted image) to `data_if_true`.
        *   Connect the final result from the "Bypass if Large" branch (e.g., the original image passed through its gate) to `data_if_false`.
        *   Connect the original `is_below_threshold` output to the `condition` input.
    *   Connect the `selected_data` output of `Select Data` to the next step (e.g., `Save Image`).
6.  Optionally, use `mask_area_percent` for display or other logic, and `mask_passthrough` if needed elsewhere.

## Example Use Cases

* **Optimize Face Detailing**: Automatically skip computationally expensive face detailing (like Face Detailer or After Detailer) if the detected face mask is already large enough (i.e., when `is_below_threshold` is `False`).
* **Conditional Image Processing**: Apply different effects or processing steps based on the size of a masked object.
* **Workflow Routing**: Direct the workflow down different paths depending on whether a detected object meets a size criterion.
* **Quality Control**: Filter out or handle masks differently if they are too small or too large for subsequent reliable processing.

## Workflow Example

Here's a conceptual outline for using the nodes to conditionally apply an inpainting process only when a mask is below a certain size threshold:

```mermaid
graph TD
    subgraph Input Data
        MaskInput[Mask Source]
        ImageInput[Image Source e.g., VAE Decode]
    end

    subgraph Condition Logic
        MAC[Mask Area Condition]
        NotBool[NOT Boolean]
        MaskInput -- MASK --> MAC
        MAC -- is_below_threshold --> NotBool
    end

    subgraph Branch - Process if SMALL (Condition TRUE)
        GateImageTrue[Gate Image Conditional]
        GateMaskTrue[Gate Mask Conditional]
        Inpaint[Inpaint Node]

        MAC -- is_below_threshold --> GateImageTrue(trigger)
        ImageInput -- IMAGE --> GateImageTrue(image)

        MAC -- is_below_threshold --> GateMaskTrue(trigger)
        MAC -- mask_passthrough --> GateMaskTrue(mask)

        GateImageTrue -- IMAGE --> Inpaint
        GateMaskTrue -- MASK --> Inpaint
    end

    subgraph Branch - Bypass if LARGE (Condition FALSE)
        GateImageFalse[Gate Image Conditional]
        NotBool -- boolean --> GateImageFalse(trigger)
        ImageInput -- IMAGE --> GateImageFalse(image)
    end

    subgraph Merge Results
        Select[Select Data based on Condition]
        Inpaint -- IMAGE --> Select(data_if_true)
        GateImageFalse -- IMAGE --> Select(data_if_false)
        MAC -- is_below_threshold --> Select(condition)
    end

    subgraph Final Output
        Save[Save Image]
        Select -- selected_data --> Save
    end

```
*   **Mask Area Condition:** Determines if the mask is small (`is_below_threshold = True`).
*   **NOT Boolean:** Inverts the condition for the "large mask" branch.
*   **Gate Nodes:** Triggered by the condition or its inverse, they pass either the real data (Image/Mask) or dummy data to their respective branches. This prevents errors in the Inpaint node if it receives no input.
*   **Inpaint Node:** Runs only with valid data if the mask is small. Receives dummy data otherwise.
*   **Select Data:** Chooses between the output of the Inpaint node (`data_if_true`) and the output of the bypass gate (`data_if_false`) based on the original `is_below_threshold` condition.
*   **Save Image:** Receives the correctly selected image.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

* [Georg Neumann](https://www.linkedin.com/in/georg-neumann) from [KI Marketing Bootcamp](https://marketing-ki.de) for the initial code and concept
* The [ComfyUI](https://github.com/comfyanonymous/ComfyUI) team and contributors for creating an amazing platform
* The vibrant [ComfyUI community](https://registry.comfy.org) and all the custom node creators who continue to push the boundaries of what's possible
* [Claude by Anthropic](https://www.anthropic.com/claude) for assistance in code refactoring, optimization, and documentation


---

Created with ❤️ for the ComfyUI community.