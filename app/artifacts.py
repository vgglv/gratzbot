class Artifact:
    def __init__(self, json: dict):
        self.name = json["name"]
        self.price = json["price"]
        self.type = json["type"]
        self.value = json["value"]
        self.description = json["description"]
        self.icon = json["icon"]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "price": self.price,
            "type": self.type,
            "value": self.value,
            "description": self.description
        }


def find_artefact_by_name(artifact_list: list[dict], target_name: str) -> Artifact:
    for artefact in artifact_list:
        if artefact["name"] == target_name:
            return Artifact(artefact)
    return None


def print_artifacts(artifact_list: list[dict]) -> str:
    result = []
    for artifact in artifact_list:
        icon = artifact["icon"]
        name = artifact["name"]
        price = artifact["price"]
        description = artifact["description"]
        result.append(f"\n{icon} {name}, цена: {price} зол. {description}")
    return "\n".join(result)