


def factory(movement=0.1):
    """
    Creates a rapid trigger function with specific actuation and reset points.
    Returns the current pressed state after evaluating the value.
    """
    state = {
        "decreasing": True,
        "last": None,
        "ref": None,
    }

    def update_trend(value):
        """Checks if value trend is decreasing based on threshold. Less than 10 lines."""
        if state['last'] is None: state['last'] = state['ref'] = value; return False # Init
        if state['decreasing']: # Currently decreasing
            if value > state['ref'] + movement: state['decreasing'], state['ref'] = False, value
            elif value < state['ref']: state['ref'] = value # Update trough
        else: # Currently increasing/stable
            if value < state['ref'] - movement: state['decreasing'], state['ref'] = True, value
            elif value > state['ref']: state['ref'] = value # Update peak
        state['last'] = value
        return not state['decreasing'] # Return current trend state

    return update_trend

    return trigger








