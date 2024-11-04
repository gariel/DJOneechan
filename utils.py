
def safe(method: callable, *args, default=None, **kwargs):
    # noinspection PyBroadException
    try:
        return method(*args, **kwargs)
    except:
        return default


def text_table(header: list[str], data: list[list[str]]) -> str:
    if not data:
        return "`no data`"

    MAX_COL_SIZE = 50
    items = [header, *data]
    ns = [
        min(
            MAX_COL_SIZE,
            max(*[
                len(items[y][x])
                for y in range(len(items))
            ])
        )
        for x in range(len(header))
    ]
    lines = [
        "| " +
        " | ".join([
            item[i].ljust(ns[i])[:ns[i]]
            for i in range(len(ns))
        ])
        + " |"
        for item in items
    ]
    bar = "+-" + "-+-".join("".ljust(n, "-") for n in ns) + "-+"
    return "```r\n" + "\n".join([
        bar,
        lines[0],
        bar.replace("-", "="),
        *lines[1:],
        bar
    ]) + "\n```"

