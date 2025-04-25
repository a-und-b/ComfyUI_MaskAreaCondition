import torch
import numpy as np

class MaskSizeDetector:
    """
    Ein ComfyUI Node, der die Größe einer Maske relativ zum Gesamtbild analysiert
    und bei Unterschreiten eines Schwellenwerts einen alternativen Workflow-Pfad auslöst.
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
                    "step": 0.1
                }),
            }
        }
    
    RETURN_TYPES = ("BOOLEAN", "FLOAT", "MASK")
    RETURN_NAMES = ("is_below_threshold", "mask_size_percent", "mask")
    FUNCTION = "check_mask_size"
    CATEGORY = "mask_operations"
    
    def check_mask_size(self, mask, threshold_percent):
        """
        Überprüft die Größe der Maske relativ zum Gesamtbild.
        
        Args:
            mask: Eingangsmaske
            threshold_percent: Schwellenwert in Prozent (0.0 - 100.0)
            
        Returns:
            is_below_threshold: Boolean, der angibt, ob die Maske kleiner als der Schwellenwert ist
            mask_size_percent: Größe der Maske in Prozent relativ zum Gesamtbild
            mask: Die ursprüngliche Maske (wird unverändert weitergegeben)
        """
        # Maske in ein NumPy-Array konvertieren, falls sie als Tensor vorliegt
        if isinstance(mask, torch.Tensor):
            mask_array = mask.cpu().numpy()
        else:
            mask_array = np.array(mask)
        
        # Anzahl der Pixel in der Maske zählen (Werte > 0 gelten als Teil der Maske)
        mask_pixels = np.sum(mask_array > 0)
        
        # Gesamtgröße des Bildes berechnen
        total_pixels = mask_array.size
        
        # Prozentsatz der Maske berechnen
        if total_pixels > 0:
            mask_size_percent = (mask_pixels / total_pixels) * 100.0
        else:
            mask_size_percent = 0.0
        
        # Überprüfen, ob die Maske kleiner als der Schwellenwert ist
        is_below_threshold = mask_size_percent < threshold_percent
        
        # Debugging-Ausgabe
        print(f"Maskengröße: {mask_size_percent:.2f}% (Schwellenwert: {threshold_percent:.2f}%)")
        print(f"Unter Schwellenwert: {is_below_threshold}")
        
        return (is_below_threshold, mask_size_percent, mask)

# Node in ComfyUI registrieren
NODE_CLASS_MAPPINGS = {
    "MaskSizeDetector": MaskSizeDetector
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MaskSizeDetector": "Mask Size Detector"
}