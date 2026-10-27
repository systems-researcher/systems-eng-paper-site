def scholar_date(value):
    text = str(value).strip()
    if len(text) == 4:
        return text
    year, month, day = text.split("-")
    return "%s/%d/%d" % (year, int(month), int(day))


def iso_date(value):
    return str(value).strip()
