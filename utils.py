# -*- coding: utf-8 -*-


# Since NoneType is not actually defined, yet is returned by 'type(None)'
NoneType = type(None)


class SlotDefinedClass(object):
    __slots__ = tuple()  # Names of attributes
    __types__ = {}  # Optional mapping of attribute to expected type
    __defaults__ = {}  # Optional default values for an attribute

    def __init__(self, *args, **kwargs):
        slots = self.__slots__
        defaults = self.__defaults__

        set_attrs = set()

        # Go through args first, then kwargs
        for i, val in enumerate(args):
            attr = slots[i]
            self.__check_and_set_attr(attr, val)
            set_attrs.add(attr)

        for attr in slots:
            if attr in set_attrs:
                # We already set this value in the args
                continue

            if attr in kwargs:
                val = kwargs[attr]
            elif attr in defaults:
                val = defaults[attr]
            else:
                raise RuntimeError("No value for attribute '{}' provided".format(attr))

            self.__check_and_set_attr(attr, val)


    def __check_and_set_attr(self, attr, val):
        if attr in self.__types__:
            self.__check_type(attr, val, self.__types__[attr])
        setattr(self, attr, val)


    def __check_type(self, attr, val, expected):
        """Check that the appropriate type is used.

        If the attribute is meant to be a container, check the contents of the
        container. In this case, just the first element of the container is
        checked.

        Args:
            attr (str)
        """
        if isinstance(expected, type):
            # Base class
            assert isinstance(val, expected), \
                "Expected type '{}' for attribute '{}'. Got '{}'".format(
                    expected, attr, type(val)
                )
        elif isinstance(expected, list):
            # Check container
            self.__check_type(attr, val, list)

            # Check elements
            if val:
                self.__check_type(attr, val[0], expected[0])
        elif isinstance(expected, dict):
            # Check container
            self.__check_type(attr, val, dict)

            # Check keys and vals
            if val:
                self.__check_type(attr, next(val.keys()), next(expected.keys()))
                self.__check_type(attr, next(val.values()), next(expected.values()))
        else:
            raise RuntimeError("Uknown type handling for type '{}'".format(expected))


def merge_dicts(d1, d2):
    d1_copy = d1.copy()
    d1_copy.update(d2)
    return d1_copy


