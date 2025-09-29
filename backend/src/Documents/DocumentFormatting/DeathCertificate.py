from dataclasses import dataclass, field
from src.Documents.Document import Document


@dataclass
class DeathCertificate(Document):
    name: str = "Certificate of Death"
    fields: list[str] = field(
        default_factory=lambda: [
            "DECEDENT'S FIRST NAME",
            "DECEDENT'S MIDDLE NAME",
            "DECEDENT'S LAST NAME",
            "DECEDENT'S SUFFIX",
            "DECEDENT's AKA'S",
            "DATE OF DEATH (mm/dd/yyyy)",
            "SEX",
            "SOCIAL SECURITY NUMBER",
            "DATE OF BIRTH (mm/dd/yyyy)",
            "AGE",
            "CITY / TOWN / COUNTY / ZIP OF DEATH LOCATION",
            "PLACE OF DEATH (FACILITY NAME AND ADDRESS)",
            "BIRTHPLACE (CITY, STATE OR COUNTRY)",
            "MARITAL STATUS",
            "NAME OF SURVIVING SPOUSE PRIOR TO FIRST MARRIAGE (FIRST, MIDDLE, LAST, SUFFIX)",
            "DECEDENT'S USUAL RESIDENCE ADDRESS (STREET, CITY, COUNTY, STATE, ZIP)",
            "DECEDENT'S HISPANIC ORIGIN(S)",
            "DECEDENT'S RACE(S)",
            "EVER IN ARMED FORCES",
            "OCCUPATION",
            "FATHER'S NAME (FIRST, MIDDLE, LAST, SUFFIX)",
            "MOTHER'S NAME PRIOR TO FIRST MARRIAGE (FIRST, MIDDLE, LAST, SUFFIX)",
            "INFORMANT'S NAME (FIRST, MIDDLE, LAST, SUFFIX)",
            "INFORMANT'S RELATIONSHIP",
            "INFORMANT'S MAILING ADDRESS",
            "FUNERAL FACILITY OR RESPONSIBLE PERSON (NAME & ADDRESS)",
            "FUNERAL DIRECTOR'S NAME OR RESPONSIBLE PERSON",
            "LICENSE NUMBER",
            "METHOD(S) OF DISPOSITION",
            "FIRST DISPOSITION FACILITY NAME & LOCATION",
            "SECOND DISPOSITION FACILITY NAME & LOCATION",
            "IMMEDIATE CAUSE OF DEATH",
            "APPROXIMATE INTERVAL (CAUSE A)",
            "DUE TO OR AS A CONSEQUENCE OF (CAUSE B)",
            "APPROXIMATE INTERVAL (CAUSE B)",
            "DUE TO OR AS A CONSEQUENCE OF (CAUSE C)",
            "APPROXIMATE INTERVAL (CAUSE C)",
            "DUE TO OR AS A CONSEQUENCE OF (CAUSE D)",
            "APPROXIMATE INTERVAL (CAUSE D)",
            "OTHER SIGNIFICANT CONDITIONS CONTRIBUTING TO DEATH",
            "INJURY?",
            "INJURY AT WORK?",
            "MANNER OF DEATH",
            "TIME OF DEATH",
            "AUTOPSY PERFORMED?",
            "AUTOPSY FINDINGS AVAILABLE?",
            "NAME OF PERSON COMPLETING CAUSE OF DEATH",
            "DATE CERTIFIED (mm/dd/yyyy)",
            "CERTIFIER'S ADDRESS",
            "DATE REGISTERED (mm/dd/yyyy)",
            "DATE ISSUED (mm/dd/yyyy)",
        ]
    )

    def __str__(self):
        return "Certificate of Death"
