import pathlib


def cut_path(path, max_size=5):
    # https://codereview.stackexchange.com/questions/169217/path-shortener-for-gui-application
    if not path:
        return path

    parts = list(pathlib.PurePath(path).parts)

    path = pathlib.PurePath(parts[0])
    for part in parts[1:-2]:
        path /= part
        if len(str(path)) >= max_size:
            path /= '...'
            break
    if len(parts) > 1:
        path /= f'{parts[-2]}/{parts[-1]}'
    return path
