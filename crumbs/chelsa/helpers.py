"""
Module declaring helper functions to read options.
"""

def get_variables_args(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

def get_timesID_args(option, opt, value, parser, type='int'):
    setattr(parser.values, option.dest, [int(s) for s in value.split(',')])
