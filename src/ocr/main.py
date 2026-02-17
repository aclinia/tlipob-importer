import json
import sys

import easyocr  # type: ignore[import-untyped]

from .ocr import process_screenshot


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <screenshot> [screenshot ...]", file=sys.stderr)
        sys.exit(1)

    reader = easyocr.Reader(["en"], gpu=True)

    for path in sys.argv[1:]:
        item = process_screenshot(path, reader)
        if item:
            if len(sys.argv) > 2:
                print(f"--- {path} ---")
            print(json.dumps(item.to_dict(), indent=2))
            print()


if __name__ == "__main__":
    main()
