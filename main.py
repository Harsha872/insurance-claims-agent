import pdfplumber
import re
import json

MANDATORY_FIELDS = [
    "Policy Number",
    "Policyholder Name",
    "Date of Loss",
    "Description",
    "Estimated Damage",
    "Claim Type"
]

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_fields(text):
    fields = {}

    def find(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    fields["Policy Number"] = find(r"POLICY NUMBER\s*:?\s*(.+)")
    fields["Policyholder Name"] = find(r"NAME OF INSURED\s*:?\s*(.+)")
    fields["Date of Loss"] = find(r"DATE OF LOSS\s*(AND TIME)?\s*:?\s*(.+)")
    fields["Location"] = find(r"LOCATION OF LOSS\s*:?\s*(.+)")
    fields["Estimated Damage"] = find(r"ESTIMATE AMOUNT\s*:?\s*(.+)")

    # Description logic
    fields["Description"] = "Automobile accident reported as per FNOL document"

    # Asset details (static assumption for demo)
    fields["Asset Type"] = "Vehicle"
    fields["Asset ID"] = find(r"V\.I\.N\.\s*:?\s*(.+)")

    # Claim type rule
    if "INJURED" in text:
        fields["Claim Type"] = "injury"
    else:
        fields["Claim Type"] = "vehicle"

    return fields


def find_missing_fields(fields):
    return [field for field in MANDATORY_FIELDS if not fields.get(field)]


def route_claim(fields, missing_fields):
    description = (fields.get("Description") or "").lower()
    damage = fields.get("Estimated Damage")

    if missing_fields:
        return "Manual Review", "One or more mandatory fields are missing"

    if any(word in description for word in ["fraud", "staged", "inconsistent"]):
        return "Investigation Flag", "Suspicious keywords found in description"

    if fields.get("Claim Type") == "injury":
        return "Specialist Queue", "Claim involves injury"

    if damage:
        try:
            damage_value = int(re.sub(r"[^\d]", "", damage))
            if damage_value < 25000:
                return "Fast-track", "Estimated damage below 25,000"
        except:
            pass

    return "Manual Review", "Could not confidently auto-route claim"


def process_claim(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    fields = extract_fields(text)
    missing = find_missing_fields(fields)
    route, reason = route_claim(fields, missing)

    return {
        "extractedFields": fields,
        "missingFields": missing,
        "recommendedRoute": route,
        "reasoning": reason
    }


if __name__ == "__main__":
    result = process_claim("sample_fnol.pdf")
    print(json.dumps(result, indent=2))

    # Save output
    with open("sample_output.json", "w") as f:
        json.dump(result, f, indent=2)
