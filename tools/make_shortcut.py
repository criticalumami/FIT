#!/usr/bin/env python3
"""Build the unsigned "FIT Upload" shortcut (share sheet: Health export.zip -> FIT-data).

    python3 tools/make_shortcut.py && shortcuts sign --mode anyone \
        --input "shortcuts/FIT Upload.unsigned.shortcut" --output "shortcuts/FIT Upload.shortcut"

The token is never stored here: Shortcuts asks for it when the shortcut is
added (import question on the first Text action). The final notification shows
GitHub's answer to the upload, so failures are visible on the phone.
"""
import os
import plistlib
import uuid

REPO = "criticalumami/FIT-data"
INBOX_RELEASE_ID = 421090352  # release tagged `inbox` in FIT-data
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "shortcuts", "FIT Upload.unsigned.shortcut")


def uid():
    return str(uuid.uuid4()).upper()


def text(string, attachments=None):
    value = {"string": string}
    if attachments:
        value["attachmentsByRange"] = attachments
    return {"Value": value, "WFSerializationType": "WFTextTokenString"}


def fields(items):
    return {"Value": {"WFDictionaryFieldValueItems": [
        {"WFItemType": 0, "WFKey": text(k), "WFValue": v} for k, v in items]},
        "WFSerializationType": "WFDictionaryFieldValue"}


token_uuid = uid()
bearer = text("Bearer ￼", {"{7, 1}": {"OutputUUID": token_uuid, "Type": "ActionOutput", "OutputName": "Text"}})
github_json = ("Accept", text("application/vnd.github+json"))

upload_uuid, state_uuid, message_uuid, size_uuid = uid(), uid(), uid(), uid()


def output(action_uuid, name):
    return {"OutputUUID": action_uuid, "Type": "ActionOutput", "OutputName": name}


def field_of_upload(key, action_uuid):
    """Get Dictionary Value <key> from the upload response (GitHub's JSON answer)."""
    return {"WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
            "WFWorkflowActionParameters": {
                "UUID": action_uuid,
                "WFGetDictionaryValueType": "Value",
                "WFDictionaryKey": key,
                "WFInput": {"Value": output(upload_uuid, "Contents of URL"),
                            "WFSerializationType": "WFTextTokenAttachment"},
            }}


# Notification shows GitHub's answer: "uploaded" + size on success, the error message otherwise.
status_text = "Upload: \ufffc\ufffc (\ufffc Bytes). Daten sind in ca. 1-2 Minuten aktualisiert."
status = text(status_text, {
    "{8, 1}": output(state_uuid, "Dictionary Value"),
    "{9, 1}": output(message_uuid, "Dictionary Value"),
    "{12, 1}": output(size_uuid, "Dictionary Value"),
})

actions = [
    {"WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
     "WFWorkflowActionParameters": {"UUID": token_uuid, "WFTextActionText": ""}},
    {"WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
     "WFWorkflowActionParameters": {
         "UUID": upload_uuid,
         "WFURL": f"https://uploads.github.com/repos/{REPO}/releases/{INBOX_RELEASE_ID}/assets?name=export.zip",
         "WFHTTPMethod": "POST",
         "ShowHeaders": True,
         "WFHTTPHeaders": fields([("Authorization", bearer), ("Content-Type", text("application/zip")), github_json]),
         "WFHTTPBodyType": "File",
         "WFRequestVariable": {"Value": {"Type": "ExtensionInput"}, "WFSerializationType": "WFTextTokenAttachment"},
     }},
    field_of_upload("state", state_uuid),
    field_of_upload("message", message_uuid),
    field_of_upload("size", size_uuid),
    {"WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
     "WFWorkflowActionParameters": {
         "UUID": uid(),
         "WFURL": f"https://api.github.com/repos/{REPO}/dispatches",
         "WFHTTPMethod": "POST",
         "ShowHeaders": True,
         "WFHTTPHeaders": fields([("Authorization", bearer), github_json]),
         "WFHTTPBodyType": "JSON",
         "WFJSONValues": fields([("event_type", text("health-export"))]),
     }},
    {"WFWorkflowActionIdentifier": "is.workflow.actions.notification",
     "WFWorkflowActionParameters": {
         "UUID": uid(),
         "WFNotificationActionTitle": "FIT",
         "WFNotificationActionBody": status,
     }},
]

workflow = {
    "WFWorkflowName": "FIT Upload",
    "WFWorkflowClientVersion": "2302.0.4",
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowIcon": {"WFWorkflowIconStartColor": 4282601983, "WFWorkflowIconGlyphNumber": 59446},
    "WFWorkflowTypes": ["ActionExtension"],  # appears in the share sheet
    "WFWorkflowInputContentItemClasses": ["WFGenericFileContentItem"],
    "WFWorkflowHasShortcutInputVariables": True,
    # Started without a file (from the Shortcuts app / Mac): ask for the export instead of sending nothing.
    "WFWorkflowNoInputBehavior": {"Name": "WFWorkflowNoInputBehaviorAskForInput",
                                  "Parameters": {"ItemClass": "WFGenericFileContentItem"}},
    "WFWorkflowOutputContentItemClasses": [],
    "WFQuickActionSurfaces": [],
    "WFWorkflowImportQuestions": [{
        "ActionIndex": 0, "Category": "Parameter", "ParameterKey": "WFTextActionText", "DefaultValue": "",
        "Text": "Füge deinen FIT-data GitHub-Token ein (beginnt mit github_pat_). / Paste your FIT-data GitHub token.",
    }],
    "WFWorkflowActions": actions,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "wb") as f:
    plistlib.dump(workflow, f, fmt=plistlib.FMT_BINARY)
print(OUT)
