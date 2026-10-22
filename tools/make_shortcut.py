#!/usr/bin/env python3
"""Build the unsigned "FIT Upload" shortcut (share sheet: Health export.zip -> FIT-data).

    python3 tools/make_shortcut.py && shortcuts sign --mode anyone \
        --input "shortcuts/FIT Upload.unsigned.shortcut" --output "shortcuts/FIT Upload.shortcut"

The token is never stored here: after adding the shortcut, paste it into the
first Text action (placeholder below). No import question: those made the
"Add Shortcut" step hang.
"""
import os
import plistlib
import uuid

REPO = "criticalumami/FIT-data"
TOKEN_PLACEHOLDER = "HIER_TOKEN_EINFUEGEN"
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

actions = [
    {"WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
     "WFWorkflowActionParameters": {"UUID": token_uuid, "WFTextActionText": TOKEN_PLACEHOLDER}},
    {"WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
     "WFWorkflowActionParameters": {
         "UUID": uid(),
         "WFURL": f"https://uploads.github.com/repos/{REPO}/releases/{INBOX_RELEASE_ID}/assets?name=export.zip",
         "WFHTTPMethod": "POST",
         "ShowHeaders": True,
         "WFHTTPHeaders": fields([("Authorization", bearer), ("Content-Type", text("application/zip")), github_json]),
         "WFHTTPBodyType": "File",
         "WFRequestVariable": {"Value": {"Type": "ExtensionInput"}, "WFSerializationType": "WFTextTokenAttachment"},
     }},
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
         "WFNotificationActionBody": "Health-Export gesendet. Deine Daten sind in ca. 1-2 Minuten aktualisiert.",
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
    "WFWorkflowOutputContentItemClasses": [],
    "WFQuickActionSurfaces": [],
    "WFWorkflowImportQuestions": [],
    "WFWorkflowActions": actions,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "wb") as f:
    plistlib.dump(workflow, f, fmt=plistlib.FMT_BINARY)
print(OUT)
