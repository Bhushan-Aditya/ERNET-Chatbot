"""
Knowledge base for ERNET domain registration chatbot
"""

DOMAIN_TYPES = {
    "ac.in": "For academic institutions",
    "edu.in": "For educational institutions",
    "res.in": "For research institutions",
    "विद्या.भारत": "For academic institutions (IDN)",
    "शिक्षा.भारत": "For educational institutions (IDN)",
    "शोध.भारत": "For research institutions (IDN)"
}

ELIGIBILITY_REQUIREMENTS = {
    "institution_types": [
        "Educational institutions affiliated/recognized by Central/State Act",
        "Institutions registered under educational boards",
        "Research institutes with government recognition",
        "Vocational/professional institutions with government affiliation",
        "Skill development organizations registered under government ministries"
    ],
    "required_documents": [
        "Application letter on institution letterhead",
        "Undertaking on Rs.100 stamp paper",
        "Affiliation/Approval letters",
        "Registration documents",
        "GSTN certificate (if applicable)"
    ]
}

DOMAIN_RULES = {
    "length": "3-63 characters",
    "allowed_characters": "letters (A-Z, a-z), digits (0-9), hyphens",
    "restrictions": [
        "Cannot begin or end with hyphens",
        "Must match institution's name",
        "Cannot use reserved names",
        "Cannot use government organization names",
        "Case insensitive"
    ]
}

REGISTRATION_POLICIES = {
    "duration": {
        "minimum": "1 year",
        "maximum": "10 years",
        "renewal_max": "9 years"
    },
    "expiry_handling": {
        "deactivation": "After 40 days of expiry",
        "deletion": "After 40 days of deactivation",
        "restoration": "Possible within 30 days of deletion"
    },
    "fees": {
        "reactivation": "Rs.1000 + GST",
        "restoration": "Rs.2500 + GST"
    }
}

VALUE_ADDED_SERVICES = {
    "WaaS": {
        "name": "Website as a Service",
        "features": [
            "Customized design",
            "User-friendly navigation",
            "Responsive and mobile-friendly",
            "Content Management System",
            "2GB base storage"
        ]
    },
    "LMaaS": {
        "name": "Learning Management as a Service",
        "features": [
            "Customizable e-learning platform",
            "User-friendly interface",
            "Mobile compatibility",
            "Multimedia support",
            "2GB base storage"
        ]
    }
}

SUPPORT_INFO = {
    "email": "helpdesk@domain.ernet.in",
    "response_time": "Within 24 hours",
    "phone_support": "Available with ticket number"
}

def get_domain_info(domain_type):
    """Get information about a specific domain type"""
    return DOMAIN_TYPES.get(domain_type, "Unknown domain type")

def get_eligibility_info():
    """Get eligibility requirements"""
    return ELIGIBILITY_REQUIREMENTS

def get_domain_rules():
    """Get domain naming rules"""
    return DOMAIN_RULES

def get_registration_policies():
    """Get registration policies"""
    return REGISTRATION_POLICIES

def get_value_added_services():
    """Get information about value added services"""
    return VALUE_ADDED_SERVICES

def get_support_info():
    """Get support contact information"""
    return SUPPORT_INFO 