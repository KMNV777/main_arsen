from quotes_bot.models import list_people


def person_name_filter():
    names = {person.name for person in list_people()}
    if not names:
        return None

    escaped = [name.replace("\\", "\\\\").replace(".", "\\.") for name in names]
    pattern = "^(" + "|".join(escaped) + ")$"
    return pattern
