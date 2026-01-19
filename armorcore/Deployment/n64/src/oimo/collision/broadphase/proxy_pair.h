#pragma once

#include "proxy.h"

typedef struct OimoProxyPair {
    struct OimoProxyPair* _next;    // Next pair in linked list

    OimoProxy* _p1;                  // First proxy
    OimoProxy* _p2;                  // Second proxy
} OimoProxyPair;

static inline void oimo_proxy_pair_init(OimoProxyPair* pair) {
    pair->_next = NULL;
    pair->_p1 = NULL;
    pair->_p2 = NULL;
}

static inline OimoProxy* oimo_proxy_pair_get_proxy1(const OimoProxyPair* pair) {
    return pair->_p1;
}

static inline OimoProxy* oimo_proxy_pair_get_proxy2(const OimoProxyPair* pair) {
    return pair->_p2;
}

static inline OimoProxyPair* oimo_proxy_pair_get_next(const OimoProxyPair* pair) {
    return pair->_next;
}

