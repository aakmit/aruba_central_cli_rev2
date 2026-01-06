from copy import deepcopy


def __setattrs__(self, config_attrs):
    """
    Utility function to dynamically set attributes of an object based on
        the provided dictionary
    :param config_attrs: dict whose keys will be added as attributes to
        the provided object with the value set to the value in config_attrs
    :type config_attrs: dict
    """
    attr_data_dict = dict()
    for key, value in config_attrs.items():
        if hasattr(self, key):
            attr_data_dict[key] = getattr(self, key)
        else:
            attr_data_dict[key] = value

    return attr_data_dict


def create_attrs(obj, data_dictionary):
    """
    Given a dictionary object creates class attributes. The methods
        implements setattr() which sets the value of the specified
        attribute of the specified object. If the attribute is already
        created within the object. It's state changes only if the current
        value is not None. Otherwise it keeps the previous value.
    :param obj: Object instance to create/set attributes
    :type obj: PYCENTRAL object
    :param data_dictionary: dictionary containing keys that will be attrs
    :type data_dictionary: dict
    """

    # Used to create a deep copy of the dictionary
    dictionary_var = deepcopy(data_dictionary)

    # K is the argument and V is the value of the given argument
    for k, v in dictionary_var.items():
        # In case a key has '-' inside it's name.
        k = k.replace("-", "_")

        obj.__dict__[k] = v
