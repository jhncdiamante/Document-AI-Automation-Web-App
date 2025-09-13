from dataclasses import dataclass, field
from backend.src.Documents.Document import Document

@dataclass
class DeathRegistrationWorksheet(Document):
    name = "Death Registration Worksheet"
    fields: list[str] = field(default_factory=lambda: [
        "DECEDENT'S LEGAL FIRST NAME",
        "DECEDENT'S LEGAL MIDDLE NAME",
        "DECEDENT'S LEGAL LAST NAME",
        "SUFFIX (JR, II, ETC)",
        "AKA'S IF ANY",
        "SEX",
        "U.S. SOCIAL SECURITY NUMBER",
        "DATE OF DEATH",
        "DATE OF BIRTH",
        "AGE IN",
        "DECEDENT'S BIRTH CITY OR TOWN",
        "DECEDENT'S BIRTH COUNTY",
        "DECEDENT'S BIRTH STATE",
        "DECEDENT'S BIRTH COUNTRY",
        "EVER IN U.S. ARMED FORCES?",
        "DECEDENT'S NAME PRIOR TO FIRST MARRIAGE",
        "HRRF (HUMAN REMAINS RELEASE FORM)",
        "DECEDENT'S RESIDENCE STREET ADDRESS",
        "ZIP CODE",
        "RESIDENCE CITY",
        "RESIDENCE COUNTY",
        "RESIDENCE STATE",
        "RESIDENCE COUNTRY",
        "IN CITY LIMITS",
        "HOW LONG IN THE STATE OF ARIZONA?",
        "RESIDED IN AZ. TRIBAL COMMUNITY?",
        "MARITAL STATUS",
        "FIRST NAME OF SURVIVING SPOUSE",
        "MIDDLE NAME OF SURVIVING SPOUSE",
        "LAST NAME OF SURVIVING SPOUSE",
        "SUFFIX (SURVIVING SPOUSE)",
        "LAST NAME OF SURVIVING SPOUSE PRIOR TO FIRST MARRIAGE",
        "FATHER'S FIRST NAME",
        "FATHER'S MIDDLE NAME",
        "FATHER'S LAST NAME",
        "SUFFIX (FATHER)",
        "MOTHER'S FIRST NAME",
        "MOTHER'S MIDDLE NAME",
        "MOTHER'S LAST NAME PRIOR TO FIRST MARRIAGE",
        "SUFFIX (MOTHER)",
        "INFORMANT'S FIRST NAME",
        "INFORMANT'S MIDDLE NAME",
        "INFORMANT'S LAST NAME",
        "SUFFIX (INFORMANT)",
    ])

    def ___str__(self):
        return "Death Registration Worksheet"