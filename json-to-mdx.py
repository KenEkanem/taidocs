import json
import os

# Load your Postman collection file
with open("api/NinComply.json", "r", encoding="utf-8") as f:
    collection = json.load(f)

output_dir = "mintlify_docs"
os.makedirs(output_dir, exist_ok=True)

def sanitize_filename(name):
    return name.lower().replace(" ", "_").replace("/", "_").replace("?", "")

def generate_param_fields(params, param_type):
    lines = []
    for param in params:
        name = param.get("key")
        value = param.get("value", "")
        required = param.get("disabled", False) is False
        type_hint = "string"  
        placeholder = f'"{value}"' if isinstance(value, str) else value

        line = f'<ParamField {param_type}="{name}" placeholder={placeholder} type="{type_hint}"'
        if required:
            line += ' required'
        line += f'>\n    {param.get("description", name)}\n</ParamField>\n'
        lines.append(line)
    return "\n".join(lines)

def generate_response_stub():
    return """### Response

<ResponseField name="message" type="string">
    Response message.
</ResponseField>

<ResponseExample>
```json Response
{
  "message": "Success"
}
```
</ResponseExample>
"""

for item in collection["item"]:
    name = item["name"]
    request = item.get("request", {})
    method = request.get("method", "GET")
    url = request.get("url", {}).get("raw", "URL_NOT_FOUND")
    description = request.get("description", "No description provided.").replace("\n", " ").replace('"', "'")

    body = request.get("body", {}).get("raw", "")
    headers = request.get("header", [])
    query_params = request.get("url", {}).get("query", [])
    body_params = request.get("body", {}).get("urlencoded", []) + request.get("body", {}).get("formdata", [])

    filename = sanitize_filename(name) + ".mdx"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"""---
title: "{name}"
api: "{method} {url}"
description: "{description}"
---

""")
        if query_params:
            f.write("### Query Parameters\n\n")
            f.write(generate_param_fields(query_params, "query"))
            f.write("\n")

        if body_params:
            f.write("### Body\n\n")
            f.write(generate_param_fields(body_params, "body"))
            f.write("\n")

        if headers:
            f.write("### Headers\n\n")
            f.write(generate_param_fields(headers, "header"))
            f.write("\n")

        f.write(generate_response_stub())

print(f"\n✅ Finished! Mintlify .mdx files saved in '{output_dir}/'")
