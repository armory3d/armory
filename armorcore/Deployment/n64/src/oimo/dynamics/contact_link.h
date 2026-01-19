#pragma once

// contact_link.h
// 1:1 port from OimoPhysics ContactLink.hx

// Forward declarations
struct OimoContact;
struct OimoRigidBody;

typedef struct OimoContactLink {
    struct OimoContactLink* _prev;
    struct OimoContactLink* _next;
    struct OimoContact* _contact;
    struct OimoRigidBody* _other;
} OimoContactLink;

static inline OimoContactLink oimo_contact_link_create(void) {
    OimoContactLink link;
    link._prev = NULL;
    link._next = NULL;
    link._contact = NULL;
    link._other = NULL;
    return link;
}

static inline struct OimoContact* oimo_contact_link_get_contact(const OimoContactLink* link) {
    return link->_contact;
}

static inline struct OimoRigidBody* oimo_contact_link_get_other(const OimoContactLink* link) {
    return link->_other;
}

static inline OimoContactLink* oimo_contact_link_get_prev(const OimoContactLink* link) {
    return link->_prev;
}

static inline OimoContactLink* oimo_contact_link_get_next(const OimoContactLink* link) {
    return link->_next;
}
