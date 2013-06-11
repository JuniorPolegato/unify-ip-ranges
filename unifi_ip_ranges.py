#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author.....: Junior Polegato
# Date.......: 11 Jun 2013
# Version....: 0.1.1
# Description: Operations with IP/mask octets and ranges
#              and unify sequential ip ranges

def validate_ip(ip):
    if ip.count('.') != 3:
        raise ValueError('IP address need to have 3 dots.')
    octets = [int(i) for i in ip.split('.')]
    if max(octets) > 255 or min(octets) < 0:
        raise ValueError('IP address octets need to be '
                                         'between 0 and 255 inclusive.')
    return octets

def ip_to_int(ip):
    octets = validate_ip(ip)
    result = 0
    for i, j in enumerate(octets[::-1]):
        result += int(j) << (8 * i)
    return result

def int_to_ip(i):
    if i < 0 or i > 0xFFFFFFFF:
        raise ValueError('Int IP address need to be '
                                            'between 0 and 4294967295.')
    octets = (i >> 24, i >> 16 & 0xFF, i >> 8 & 0xFF, i & 0xFF)
    return "%i.%i.%i.%i" % octets

def mask_to_int(mask):
    int_mask = ip_to_int(mask)
    strip_mask = bin(int_mask)[2:].rstrip('0')
    if '0' in strip_mask:
        raise ValueError('Mask need to be a sequence of 1 and 0 bits.')
    return int_mask

def bits_mask_to_int(bits):
    if isinstance(bits, (str, unicode)):
        bits = int(bits)
    if bits < 0 or bits > 32:
        raise ValueError('Bits mask need to be '
                                          'between 0 and 32 inclusive.')
    return (0xFFFFFFFF << (32 - bits)) & 0xFFFFFFFF

def int_to_bits_mask(i):
    if i < 0 or i > 0xFFFFFFFF:
        raise ValueError('Int mask need to be '
                                            'between 0 and 4294967295.')
    strip_mask = bin(i)[2:].rstrip('0')
    if '0' in strip_mask:
        raise ValueError('Mask need to be a sequence of 1 and 0 bits.')
    return len(strip_mask)

def ip_range(ip_mask): # ip/mask
    if ip_mask.count('/') != 1:
        raise ValueError('IP/mask format invalid.')
    ip, mask = ip_mask.split('/', 1)
    int_ip = ip_to_int(ip)
    if mask.count('.'):
        int_mask = mask_to_int(mask)
    else:
        int_mask = bits_mask_to_int(mask)
    int_first = int_ip & int_mask
    int_last = int_ip | (int_mask ^ 0xFFFFFFFF)
    first = int_to_ip(int_first)
    last = int_to_ip(int_last)
    return ((ip, int_ip),
            (int_to_ip(int_mask), int_mask, int_to_bits_mask(int_mask)),
            (first, int_first), (last, int_last))

def unify_ranges_pass(list_of_ips_mask, debug = False):
    if debug: print '-' * 80
    list_ranges = [ip_range(ip_mask) for ip_mask in list_of_ips_mask]
    list_ranges.sort(key = lambda x: x[2][1])
    before = list_ranges.pop(0)
    final = []
    for now in list_ranges:
        if debug:
            print 'before:', before
            print 'now...:', now
        if now[1][2] == before[1][2] and now[2][1] == before[3][1] + 1:
            new_mask = now[1][2] - 1
            new_range = ip_range("%s/%i" % (now[0][0], new_mask))
            if debug:
                print 'new_mask:', new_mask
                print 'new_range:', new_range
            if (before[2][1] == new_range[2][1] and
                                          now[3][1] == new_range[3][1]):
                before = new_range
                continue
        if before[2][1] >= now[2][1] and before[3][1] <= now[3][1]:
            if debug: print 'now contains before'
            before = now
            continue # before contains now
        if before[2][1] <= now[2][1] and before[3][1] >= now[3][1]:
            if debug: print 'before contains now'
            continue
        final.append(before)
        before = now
    final.append(before)
    return final

def unify_ranges(list_of_ips_mask, debug = False):
    before = None
    new = unify_ranges_pass(list_of_ips_mask, debug)
    while before != new:
        before = new
        new = unify_ranges_pass(["%s/%i" % (n[0][0], n[1][2])
                                                   for n in new], debug)
    return new

if __name__ == "__main__":
    ip_mask = '192.168.1.104/24'
    r = ip_range(ip_mask)
    print '=' * 80
    print "Range of `%s/%s(%i)´: `%s´ - `%s´ - %i address(es)." % (
                                      r[0][0], r[1][0], r[1][2],r[2][0],
                                         r[3][0], r[3][1] - r[2][1] + 1)
    print '=' * 80
    ranges = ('192.168.1.104/24', '192.168.0.104/24',
              '192.168.2.104/24', '192.168.0.104/23',
              '192.168.3.104/24', '192.168.5.111/22',
              '187.123.96.0/20')
    new_ranges = unify_ranges(ranges, True)
    print '=' * 80
    print 'Results ' * 10
    print '=' * 80
    for _range in new_ranges:
        print _range
