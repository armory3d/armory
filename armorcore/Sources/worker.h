#pragma once

#include <v8.h>

void bind_worker_class(v8::Isolate* isolate, const v8::Global<v8::Context>& context);
void handle_worker_messages(v8::Isolate* isolate, const v8::Global<v8::Context>& context);
