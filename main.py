import os
import sys

# Suppress verbose gRPC/absl logs before initializing Google libraries
os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
os.environ.setdefault("GLOG_minloglevel", "2")

from pathlib import Path
from chain import water_assessment_chain
from schemas import WaterAssessment


def main():
    """Main execution entry point for AquaSafe AI visual water assessment."""
    # Determine image path from command-line argument or default sample
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        default_sample = Path(__file__).parent / "sample_water.jpg"
        if default_sample.exists():
            image_path = str(default_sample)
        else:
            print("Usage: python main.py <path_to_water_image.jpg>")
            print("No image path provided and default sample_water.jpg not found.")
            sys.exit(1)

    print(f"Analyzing water image: {image_path}\n")

    try:
        # Run LCEL inference pipeline
        result: WaterAssessment = water_assessment_chain.invoke(image_path)

        print("=== Assessment Result ===")
        print(f"Result: {result}")
        print(f"Result Type: {type(result)}")
        print(f"\nBreakdown:")
        print(f"  • Visually Safe Confidence:   {result.visually_safe:.1f}%")
        print(f"  • Visually Risky Confidence:  {result.visually_risky:.1f}%")
        print(f"  • Image Quality Confidence:   {result.image_quality:.1f}%")
        print(f"\nVisual Analysis & Safety Guidance:")
        print(f"  {result.description}")
        print("\nNote: This is a visual-only assessment and does NOT determine potability or chemical/biological safety.")

    except FileNotFoundError as err:
        print(f"[Error] File not found: {err}")
        sys.exit(1)
    except ValueError as err:
        print(f"[Error] Invalid input or configuration: {err}")
        sys.exit(1)
    except Exception as err:
        print(f"[Error] Assessment failed: {err}")
        sys.exit(1)



if __name__ == "__main__":
    main()
