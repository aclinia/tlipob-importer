import json
import os
import sys

os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

from paddleocr import PaddleOCR  # type: ignore[import-untyped]

from .ocr import process_screenshot


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <screenshot> [screenshot ...]", file=sys.stderr)
        sys.exit(1)

    reader = PaddleOCR(
        lang="en",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    for path in sys.argv[1:]:
        item = process_screenshot(path, reader)
        if item:
            if len(sys.argv) > 2:
                print(f"--- {path} ---")
            print(json.dumps(item.to_dict(), indent=2))
            print()


if __name__ == "__main__":
    main()
