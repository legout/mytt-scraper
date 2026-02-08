"""General utility functions for mytt_scraper"""

import json


def parse_multipart_json(response_text):
    """
    Parse a response that may contain JSON followed by other data.

    Args:
        response_text: Response text that starts with JSON

    Returns:
        Tuple of (parsed_json, remaining_text)
    """
    brace_count = 0
    in_string = False
    escape_next = False
    json_end = -1

    for i, char in enumerate(response_text):
        if escape_next:
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break

    json_str = response_text[:json_end]
    remaining = response_text[json_end:]

    return json.loads(json_str), remaining
