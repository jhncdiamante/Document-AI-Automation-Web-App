from dataclasses import dataclass, field
from backend.src.Documents.Document import Document

@dataclass
class DeathRegistrationWorksheet(Document):
    name = "Death Registration Worksheet"
    fields: list[str] = field(default_factory=lambda: [
        "1A: DECEDENT'S LEGAL FIRST NAME",
        "1B: DECEDENT'S LEGAL MIDDLE NAME",
        "1C: DECEDENT'S LEGAL LAST NAME",
        "1D: SUFFIX (JR, II, ETC)",
        "1E: AKA'S IF ANY",
        "2: SEX",
        "3: U.S. SOCIAL SECURITY NUMBER",
        "4: DATE OF DEATH",
        "5A: DATE OF BIRTH",
        "5B: AGE IN",
        "6A: DECEDENT'S BIRTH CITY OR TOWN",
        "6B: DECEDENT'S BIRTH COUNTY",
        "6C: DECEDENT'S BIRTH STATE",
        "6D: DECEDENT'S BIRTH COUNTRY",
        "7: EVER IN U.S. ARMED FORCES?",
        "8: DECEDENT'S NAME PRIOR TO FIRST MARRIAGE",
        "9: HRRF (HUMAN REMAINS RELEASE FORM)",
        "10A: DECEDENT'S RESIDENCE STREET ADDRESS",
        "10B: ZIP CODE",
        "10C: RESIDENCE CITY",
        "10D: RESIDENCE COUNTY",
        "10E: RESIDENCE STATE",
        "10F: RESIDENCE COUNTRY",
        "11: IN CITY LIMITS",
        "12: HOW LONG IN THE STATE OF ARIZONA?",
        "13: RESIDED IN AZ. TRIBAL COMMUNITY?",
        "14: MARITAL STATUS",
        "15A: FIRST NAME OF SURVIVING SPOUSE",
        "15B: MIDDLE NAME OF SURVIVING SPOUSE",
        "15C: LAST NAME OF SURVIVING SPOUSE",
        "15D: SUFFIX (SURVIVING SPOUSE)",
        "15E: LAST NAME OF SURVIVING SPOUSE PRIOR TO FIRST MARRIAGE",
        "16A: FATHER'S FIRST NAME",
        "16B: FATHER'S MIDDLE NAME",
        "16C: FATHER'S LAST NAME",
        "16D: SUFFIX (FATHER)",
        "17A: MOTHER'S FIRST NAME",
        "17B: MOTHER'S MIDDLE NAME",
        "17C: MOTHER'S LAST NAME PRIOR TO FIRST MARRIAGE",
        "17D: SUFFIX (MOTHER)",
        "18A: INFORMANT'S FIRST NAME",
        "18B: INFORMANT'S MIDDLE NAME",
        "18C: INFORMANT'S LAST NAME",
        "18D: SUFFIX (INFORMANT)",
    ])

    def ___str__(self):
        return "Death Registration Worksheet"