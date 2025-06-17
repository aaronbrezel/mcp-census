from collections import deque

geography_hierarchy_key = {
    "us": {},
    "region": {},
    "division": {},
    "state": {
        "county": {
            "county subdivision": {
                "required_parent_hierarchies": ["state"],
                "subminor civil division": {
                    "required_parent_hierarchies": [
                        "state",
                        "county",
                        "county subdivision",
                    ],
                },
            },
            "tract": {
                "required_parent_hierarchies": ["state"],
            },
        },
        "place": {},
        "consolidated city": {},
        "alaska native regional corporation": {},
        "american indian area/alaska native area/hawaiian home land (or part)": {
            "required_parent_hierarchies": ["state"],
            "tribal subdivision/remainder (or part)": {
                "required_parent_hierarchies": [
                    "state",
                    "american indian area/alaska native area/hawaiian home land (or part)",
                ]
            },
        },
        "metropolitan statistical area/micropolitan statistical area (or part)": {
            "required_parent_hierarchies": ["state"],
            "principal city (or part)": {
                "required_parent_hierarchies": [
                    "state",
                    "metropolitan statistical area/micropolitan statistical area (or part)",
                ]
            },
            "metropolitan division (or part)": {
                "required_parent_hierarchies": [
                    "state",
                    "metropolitan statistical area/micropolitan statistical area (or part)",
                ]
            },
        },
        "combined statistical area (or part)": {
            "required_parent_hierarchies": ["state"]
        },
        "combined new england city and town area (or part)": {
            "required_parent_hierarchies": ["state"],
        },
        "new england city and town area (or part)": {
            "required_parent_hierarchies": ["state"],
            "principal city": {
                "required_parent_hierarchies": [
                    "state",
                    "new england city and town area (or part)",
                ]
            },
            "necta division (or part)": {
                "required_parent_hierarchies": [
                    "state",
                    "new england city and town area (or part)",
                ]
            },
        },
        "congressional district": {},
        "state legislative district (upper chamber)": {
            "required_parent_hierarchies": ["state"]
        },
        "state legislative district (lower chamber)": {
            "required_parent_hierarchies": ["state"]
        },
        "zip code tabulation area (or part)": {
            "required_parent_hierarchies": ["state"]
        },
        "school district (elementary)": {},
        "school district (secondary)": {},
        "school district (unified)": {},
    },
    "american indian area/alaska native area/hawaiian home land": {
        "tribal subdivision/remainder": {},
        "tribal census tract": {
            "required_parent_hierarchies": [
                "american indian area/alaska native area/hawaiian home land"
            ]
        },
    },
    "metropolitan statistical area/micropolitan statistical area": {
        "state (or part)": {
            "principal city (or part)": {
                "required_parent_hierarchies": [
                    "metropolitan statistical area/micropolitan statistical area",
                    "state (or part)",
                ]
            }
        },
        "metropolitan division": {
            "required_parent_hierarchies": [
                "metropolitan statistical area/micropolitan statistical area"
            ]
        },
    },
    "combined statistical area": {},
    "combined new england city and town area": {},
    "new england city and town area": {
        "state (or part)": {
            "principal city": {
                "required_parent_hierarchies": [
                    "new england city and town area",
                    "state (or part)",
                ]
            }
        },
        "necta division": {
            "required_parent_hierarchies": ["new england city and town area"]
        },
    },
    "zip code tabulation area": {},
}


def find_required_parent_geographies(target_key: str) -> list[str | None]:
    """ """
    required_parent_hierarchies: list = []

    queue = deque([(geography_hierarchy_key, None)])  # (current_dict, parent_key)

    while queue:
        current, _ = queue.popleft()

        for key, value in current.items():
            if key == target_key:
                # Found the target
                if isinstance(value, dict) and "required_parent_hierarchies" in value:
                    required_parent_hierarchies = value["required_parent_hierarchies"]
                    return required_parent_hierarchies
                else:
                    return required_parent_hierarchies  # Key found, but no required_in_clauses
            if isinstance(value, dict):
                queue.append((value, key))

    return required_parent_hierarchies


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
