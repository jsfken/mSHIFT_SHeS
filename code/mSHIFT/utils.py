import argparse



def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        print('Got v with type:')
        print(type(v))
        print('Value: %s' % v)
        raise argparse.ArgumentTypeError('Boolean value expected.')
