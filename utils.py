from collections import deque

# We'll want to flesh this out with details on how to query fips codes for this geographic hierarchy
geography_hierarchy_key = {
    "us": {},
    "region": {},
    "division": {},
    "state": {
        "county": {
            "county subdivision": {
                "required_in_clauses": ["state"],
                "subminor civil division": {
                    "required_in_clauses": ["state", "county", "county subdivision"],
                },
            },
            "tract": {
                "required_in_clauses": ["state"],
            },
        },
        "place": {},
        "consolidated city": {},
        "alaska native regional corporation": {},
        "american indian area/alaska native area/hawaiian home land (or part)": {
            "required_in_clauses": ["state"],
            "tribal subdivision/remainder (or part)": {
                "required_in_clauses": [
                    "state",
                    "american indian area/alaska native area/hawaiian home land (or part)",
                ]
            },
        },
        "metropolitan statistical area/micropolitan statistical area (or part)": {
            "required_in_clauses": ["state"],
            "principal city (or part)": {
                "required_in_clauses": [
                    "state",
                    "metropolitan statistical area/micropolitan statistical area (or part)",
                ]
            },
            "metropolitan division (or part)": {
                "required_in_clauses": [
                    "state",
                    "metropolitan statistical area/micropolitan statistical area (or part)",
                ]
            },
        },
        "combined statistical area (or part)": {"required_in_clauses": ["state"]},
        "combined new england city and town area (or part)": {
            "required_in_clauses": ["state"],
        },
        "new england city and town area (or part)": {
            "required_in_clauses": ["state"],
            "principal city": {
                "required_in_clauses": [
                    "state",
                    "new england city and town area (or part)",
                ]
            },
            "necta division (or part)": {
                "required_in_clauses": [
                    "state",
                    "new england city and town area (or part)",
                ]
            },
        },
        "congressional district": {},
        "state legislative district (upper chamber)": {
            "required_in_clauses": ["state"]
        },
        "state legislative district (lower chamber)": {
            "required_in_clauses": ["state"]
        },
        "zip code tabulation area (or part)": {"required_in_clauses": ["state"]},
        "school district (elementary)": {},
        "school district (secondary)": {},
        "school district (unified)": {},
    },
    "american indian area/alaska native area/hawaiian home land": {
        "tribal subdivision/remainder": {},
        "tribal census tract": {
            "required_in_clauses": [
                "american indian area/alaska native area/hawaiian home land"
            ]
        },
    },
    "metropolitan statistical area/micropolitan statistical area": {
        "state (or part)": {
            "principal city (or part)": {
                "required_in_clauses": [
                    "metropolitan statistical area/micropolitan statistical area",
                    "state (or part)",
                ]
            }
        },
        "metropolitan division": {
            "required_in_clauses": [
                "metropolitan statistical area/micropolitan statistical area"
            ]
        },
    },
    "combined statistical area": {},
    "combined new england city and town area": {},
    "new england city and town area": {
        "state (or part)": {
            "principal city": {
                "required_in_clauses": [
                    "new england city and town area",
                    "state (or part)",
                ]
            }
        },
        "necta division": {"required_in_clauses": ["new england city and town area"]},
    },
    "zip code tabulation area": {},
}


def convert_state_name_to_postal_abbreviation(state_name: str) -> str:
    """
    Converts a full state name to its two-letter Postal Service abbreviation.

    Args:
        state_name (str): Full name of the state (e.g., 'California').

    Returns:
        str: Two-letter state postal abbreviation (e.g., 'CA').
    """
    lookup_dict = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "District of Columbia": "DC",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
        "American Samoa": "AS",
        "Guam": "GU",
        "Northern Mariana Islands": "MP",
        "Puerto Rico": "PR",
        "U.S. Minor Outlying Islands": "UM",
        "U.S. Virgin Islands": "VI",
    }
    return lookup_dict[state_name]


def find_key_depth(d: dict, target: str, depth: int = 0) -> int | None:
    for key, value in d.items():
        if key == target:
            return depth
        if isinstance(value, dict):
            found = find_key_depth(value, target, depth + 1)
            if found is not None:
                return found


def build_fips_lookup(data: list[list[str]]) -> dict[str, dict[str, str]]:
    """
    I am unsure whether we want to include all of the geography hierarchy in the lookup.
    Or just thhe specific geography hierarchy that is being queried.
    """
    header, *rows = data

    # Build the lookup dictionary
    return {
        row[0]: {col: row[idx] for idx, col in enumerate(header) if idx != 0}
        for row in rows
    }


def find_required_in_clauses(target_key: str) -> list[str]:
    queue = deque([(geography_hierarchy_key, None)])  # (current_dict, parent_key)

    while queue:
        current, _ = queue.popleft()

        for key, value in current.items():
            if key == target_key:
                # Found the target
                if isinstance(value, dict) and "required_in_clauses" in value:
                    return value["required_in_clauses"]
                else:
                    return []  # Key found, but no required_in_clauses
            if isinstance(value, dict):
                queue.append((value, key))
