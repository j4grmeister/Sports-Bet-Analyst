def print_progress_bar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """Call in a loop to create a terminal progress bar.

    Parameters
    ----------
    iteration : int
        Current iteration.
    total : int
        Total iterations.
    prefix : str, optional
        Prefix string, by default ''.
    suffix : str, optional
        Suffix string, by default ''.
    decimals : int, optional
        Positive number of decimals in percent complete, by default 1.
    length : int, optional
        Character length of bar, by default 100.
    fill : str, optional
        Bar fill character, by default '█'.
    printEnd : str, optional
        End character, by default "\r".
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()